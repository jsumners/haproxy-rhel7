FROM centos:7

RUN yum -y install rpmdevtools '@Development tools' openssl-devel wget \
  pcre-devel zlib-devel which

RUN mkdir /output

WORKDIR /build
COPY build.sh .
RUN mkdir files
COPY files/* files/
RUN ./build.sh

CMD cp rpmbuild/RPMS/x86_64/*.rpm /output

# Mount the volume so the rpms are copied to the host.
# Must be after the files are copied to the destination or the state
# will not persist to the host.
VOLUME /output
