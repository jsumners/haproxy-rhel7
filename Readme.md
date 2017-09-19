This repository provides a script for building an up-to-date HAProxy RPM for
RHEL7 systems. Why in the hell they still package 1.5 is a mystery.

This RPM also adds some extra optimizations like JIT PCRE and
TCP Fast Open.

Other than that, it's a mashup of the upstream sources and the CentOS source
found at https://git.centos.org/tree/rpms!haproxy.git/c7

Starting with v1.7.9, you can find an unsigned RPM on the repository's
[releases page](/releases).

## Important

The resulting RPM name, and yum installable name, is "haproxy-jbs" ("jbs" being
this project author's initials). The installed binaries are still their standard names,
e.g. "haproxy". Thus, the resulting RPM conflicts with the Red Hat provided RPM.

But, again, why you would ever install that ancient build is beyond the
understanding of this author.

## Docker

You can use Docker to build the RPM:

1. `docker build --squash -t haproxy-rhel7 .`
2. `docker run -v /tmp:/output -it --rm haproxy-rhel7`
3. Look in your `/tmp` for the RPMs 😄

Note: you may want to do a `docker prune` afterward to clean up.
