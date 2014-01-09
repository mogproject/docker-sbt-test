#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
docker-sbt-test

Execute parallel 'sbt test' tasks with Docker containers.
"""

from multiprocessing import Pool
import subprocess
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import sys
from time import time
import re
import logging
from optparse import OptionParser

# Define funcion for python 2.6
try:
    subprocess.check_output
except:
    def check_output(*popenargs, **kwargs):
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            error = subprocess.CalledProcessError(retcode, cmd)
            error.output = output
            raise error
        return output
    subprocess.check_output = check_output

# Logger settings.
logger = logging.getLogger("docker-sbt-test")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Define errors.
class Error(Exception): pass
class TestNamesNotFoundError(Error): pass


class DockerProcessor:
    def __init__(self, proj_dir, repository, base_tag):
        self.proj_dir = proj_dir
        self.repository = repository
        self.base_tag = base_tag
        self.test_tag = 'test-%s' % time()

    def create_test_image(self, setup_command):
        def make_doc(tag, command):
            return 'FROM %s:%s\nRUN /bin/bash -c "%s"\n' % (self.repository, tag, command)

        def make_setup_doc():
            if setup_command:
                return make_doc(self.base_tag, setup_command.replace('\n', ' '))
            else:
                return None

        compile_doc = make_doc(self.test_tag, 'cd %s && sbt compile test:compile' % self.proj_dir)

        def f(doc):
            args = ['docker', 'build', '-rm', '-t', '%s:%s' % (self.repository, self.test_tag), '-']

            try:
                p = Popen(args, stdin=PIPE, stderr=STDOUT)
                output = p.communicate(input=doc)

                if p.returncode:
                    raise CalledProcessError(p.returncode, args)
            except EnvironmentError, e:
                raise CalledProcessError(e.errno, args)

        try:
            logger.info('Creating test image (%s:%s) ...' % (self.repository, self.test_tag))
            f(make_setup_doc())

            logger.info('Compiling...')
            f(compile_doc)
        except CalledProcessError, e:
            logger.error('Failed to create test image: %s' % e)
            raise e

    def delete_test_image(self):
        try:
            logger.info('Removing test image (%s:%s) ...' % (self.repository, self.test_tag))
            subprocess.check_call(['docker', 'rmi', '%s:%s' % (self.repository, self.test_tag)])
        except CalledProcessError, e:
            logger.info('Failed to delete test image: %s' % e)
            raise e

    def get_test_names(self):
        # Watch out for the escape sequence.
        pattern = re.compile('.*List\((.*)\).*')

        args = ['docker', 'run', '-rm',
                '-w=%s' % self.proj_dir,
                '%s:%s' % (self.repository, self.test_tag),
                "sbt 'show test:defined-test-names'"]

        try:
            logger.info('Getting test class names...')

            output = subprocess.check_output(args, stderr=STDOUT)
            logger.debug(output)

            for line in output.split('\n'):
                m = pattern.match(line)
                if m:
                    return m.group(1).split(', ')
            logger.warning('Failed to get valid output of test names.')
            raise TestNamesNotFoundError
        except CalledProcessError, e:
            logger.warning('Failed to get test names: %s' % e)
            raise e

    def test_parallel(self, test_names):
        # The number of worker processes is same as the number of CPUs.
        pool = Pool()
        result = pool.map_async(sbt_test_only, ((x, self.proj_dir, self.repository, self.test_tag) for x in test_names))
        return result.get(timeout=3600)


def sbt_test_only(params):
    test_name, proj_dir, repository, tag = params

    args = ['docker', 'run', '-rm',
            '-w=%s' % proj_dir,
            '%s:%s' % (repository, tag),
            "sbt 'test-only %s'" % test_name]

    ret = 0
    try:
        logger.info("Starting sbt 'test-only %s' ..." % test_name)
        output = subprocess.check_output(args, stderr=STDOUT)
        logger.info("Finished sbt 'test-only %s' ..." % test_name)
        print(output)
    except CalledProcessError, e:
        logger.warning("Failed sbt 'test-only %s' ..." % test_name)
        ret = e.returncode
    return ret


def main():
    def parse_args():
        usage = 'Usage: %prog REPOSITORY[:TAG] [options]'
        parser = OptionParser(usage)
        parser.add_option('-d', '--dir', dest='dir', default='.',
                          help='path to the sbt project directory in the container')
        parser.add_option('-s', '--setup', action='store', dest='setup', default='',
                          help='commands to be executed in the shell before testing')
        (options, args) = parser.parse_args()

        if len(args) != 1:
            parser.print_help()
            return None
        repos = args[0].split(':')
        if len(repos) >= 3:
            parser.error('invalid repository or tag')
            return None
        repo, tag = repos[0], 'latest' if len(repos) == 1 else repos[1]

        return (repo, tag, options.dir, options.setup)

    # Parse command line arguments.
    args = parse_args()
    if args:
        repo, tag, proj_dir, setup = args
    else:
        return 2

    d = DockerProcessor(proj_dir, repo, tag)

    ret = 0
    try:
        d.create_test_image(setup)
        test_names = d.get_test_names()
        result = d.test_parallel(test_names)

        logger.info('*** SUMMARY ***')
        for t, r in zip(test_names, result):
            if r:
                logger.warning('%s -> %s' % (t, 'NG'))
                ret = 1
            else:
                logger.info('%s -> %s' % (t, 'OK'))

        logger.info('*' * 15)

    finally:
        try:
            d.delete_test_image()
        except Exception, e:
            logger.error('Failed to delete test image: %s' % e)
            
    return ret


if __name__ == '__main__':
    sys.exit(main())
