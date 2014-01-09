docker-sbt-test
====

Execute parallel ```sbt test``` tasks with Docker containers.  
Each test is executed in the individual and clean container.


## Usage

```
Usage: docker_sbt_test.py REPOSITORY[:TAG] [options]

Options:
  -h, --help            show this help message and exit
  -d DIR, --dir=DIR     path to the sbt project directory in the container
  -s SETUP, --setup=SETUP
                        commands to be executed in the shell before testing
```

## Example

See ```example``` directory.
