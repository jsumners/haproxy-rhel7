#!/bin/bash

# TODO: add lua building

haproxyVersion="1.7.9"
luaVersion="5.3.4"

haproxyUrl="http://www.haproxy.org/download/${haproxyVersion:0:3}/src/haproxy-${haproxyVersion}.tar.gz"
luaUrl="http://www.lua.org/ftp/lua-${luaVersion}.tar.gz"

which wget > /dev/null
if [ $? -ne 0 ]; then
  echo "Aborting. Cannot continue without wget."
  exit 1
fi

which rpmbuild > /dev/null
if [ $? -ne 0 ]; then
  echo "Aborting. Cannot continue without rpmbuild. Please install the rpmdevtools package."
  exit 1
fi

# Let's get down to business
TOPDIR=$(pwd)

function buildit {
  if [ -f ${TOPDIR}/gpg-env ]; then
    source ${TOPDIR}/gpg-env
    echo "Building signed RPM..."
    if [ "${gpg_bin}" != "" ]; then
      rpmbuild --define "_topdir ${TOPDIR}/rpmbuild" --define "_signature ${signature}" \
        --define "_gpg_path ${gpg_path}" --define "_gpg_name ${gpg_name}" \
        --define "__gpg ${gpg_bin}" --sign -ba $1
    else
      rpmbuild --define "_topdir ${TOPDIR}/rpmbuild" --define "_signature ${signature}" \
        --define "_gpg_path ${gpg_path}" --define "_gpg_name ${gpg_name}" \
        --sign -ba $1
    fi
  else
    echo "Building unsigned RPM..."
    rpmbuild --define "_topdir ${TOPDIR}/rpmbuild" -ba $1
  fi

  if [ $? -ne 0 ]; then
    echo "Build failed. Exiting..."
    exit 1
  fi
}

LIBS=(
  'pcre-devel'
  'openssl-devel'
  'zlib-devel'
)
NEEDSLIBS=''
for l in ${LIBS[@]}; do
  echo "Checking for library: ${l}"
  rpm -qa | egrep $l 2>&1 >/dev/null
  if [ $? -ne 0 ]; then
    NEEDSLIBS="${l},${NEEDSLIBS}"
  fi
done
if [ "${NEEDSLIBS}" != '' ]; then
  echo "Need libraries: ${NEEDSLIBS:0:(${#NEEDSLIBS} - 1)}"
  exit 1
fi

if [ -e rpmbuild ]; then
  rm -rf rpmbuild/* 2>&1 > /dev/null
fi

echo "Creating RPM build path structure..."
mkdir -p rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS,tmp}

echo "Building HAProxy RPM ..."
cp ${TOPDIR}/files/haproxy.{cfg,logrotate,service,sysconfig} ${TOPDIR}/rpmbuild/SOURCES/
cp ${TOPDIR}/files/haproxy.spec ${TOPDIR}/rpmbuild/SPECS/

sed -i 's/~haproxyVersion~/'${haproxyVersion}'/' ${TOPDIR}/rpmbuild/SPECS/haproxy.spec

cd ${TOPDIR}/rpmbuild/SOURCES/
wget ${haproxyUrl}

cd ${TOPDIR}/rpmbuild/
buildit "SPECS/haproxy.spec"
