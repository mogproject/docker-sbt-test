Parallel testing example
----

## Requirement

* Install docker.
* Install Python 2.x (>= 2.6)


## Example

Work in the docker host.


### 1. Create base image.

The repository name to set is ```local/sbt-test``` here.

```
$ cd path/to/the/work/directory
$ git clone https://github.com/mogproject/docker-sbt-test.git
$ cd docker-sbt-test/example/docker
$ docker build -t local/sbt-test .
```

```docker build``` will take several minutes.


### 2. Run parallel test.

```
$ cd path/to/the/work/directory
$ cd docker-sbt-test
$ ./docker_sbt_test.py local/sbt-test \
--dir /workspace/docker-sbt-test/example \
--setup " \
rm -fr /workspace/docker-sbt-test && \
git clone --depth 1 https://github.com/mogproject/docker-sbt-test.git /workspace/docker-sbt-test \
"
```
