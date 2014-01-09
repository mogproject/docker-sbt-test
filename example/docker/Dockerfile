# Dockerfile for sbt test


FROM centos:6.4

# install java and git
RUN yum install -y --nogpgcheck java-1.7.0-openjdk git

# install sbt 13.1
RUN \
  wget -P /tmp http://scalasbt.artifactoryonline.com/scalasbt/sbt-native-packages/org/scala-sbt/sbt/0.13.1/sbt.rpm && \
  rpm -ivh /tmp/sbt.rpm && \
  rm -f /tmp/sbt.rpm

# install redis-server
RUN \
  wget -P /tmp http://ftp-srv2.kddilabs.jp/Linux/distributions/fedora/epel/6/x86_64/epel-release-6-8.noarch.rpm && \
  rpm -ivh /tmp/epel-release-6-8.noarch.rpm && \
  rm -f /tmp/epel-release-6-8.noarch.rpm && \
  yum install -y --nogpgcheck redis

# clone and compile sbt project
RUN \
  mkdir -p /workspace && \
  git clone https://github.com/mogproject/docker-sbt-test.git /workspace/docker-sbt-test && \
  cd /workspace/docker-sbt-test/example && \
  sbt compile test:compile 2>&1

# launch redis server when the bash starts
RUN echo "service redis start" >> /.bash_profile

# entry point
ENTRYPOINT ["/bin/bash", "-l", "-c"]
