%define haproxy_user    haproxy
%define haproxy_uid     188
%define haproxy_group   haproxy
%define haproxy_gid     188
%define haproxy_home    %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy
%define haproxy_datadir %{_datadir}/haproxy

%define version ~haproxyVersion~
#%define dev_rel dev25
#%define release 1

Name: haproxy-jbs
Summary: HA-Proxy is a TCP/HTTP reverse proxy for high availability environments
Version: %{version}
Release: %{release}%{?dist}
License: GPLv2+
URL: http://www.haproxy.org/
Group: System Environment/Daemons
Provides: haproxy
Conflicts: haproxy-1.5

Source0: http://www.haproxy.org/download/1.7/src/haproxy-%{version}.tar.gz
Source1: haproxy.service
Source2: haproxy.cfg
Source3: haproxy.logrotate
Source4: haproxy.sysconfig

Requires(pre): %{_sbindir}/groupadd
Requires(pre): %{_sbindir}/useradd
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(postun): /sbin/service

BuildRoot: %{_tmppath}/haproxy-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: pcre-devel openssl-devel zlib-devel systemd-units
BuildRequires: setup >= 2.5
Requires: pcre openssl zlib

Requires(pre): shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
HAProxy is a free, fast and reliable solution offering high
availability, load balancing, and proxying for TCP and HTTP-based
applications. It is particularly suited for web sites crawling under
very high loads while needing persistence or Layer7 processing.
Supporting tens of thousands of connections is clearly realistic with
modern hardware. Its mode of operation makes integration with existing
architectures very easy and riskless, while still offering the
possibility not to expose fragile web servers to the net.

%prep
%setup -q -n haproxy-%{version}

%build
%ifarch %ix86 x86_64
use_regparm="USE_REGPARM=1"
%endif

# TODO: add USE_LUA=1
make %{?_smp_mflags} CPU="generic" TARGET="linux2628" \
  USE_PCRE=1  USE_PCRE_JIT=1 \
  USE_OPENSSL=1 USE_ZLIB=1  \
  USE_TFO=1 USE_VSYSCALL=1 US_NS=1 \
  ${use_regparm}

pushd contrib/halog
%{__make} halog OPTIMIZE="%{optflags}"
popd

pushd contrib/iprange
%{__make} iprange OPTIMIZE="${optflags}"
popd

%install
rm -rf %{buildroot}
make install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix} TARGET="linux2628"
make install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}

%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/haproxy.service
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{haproxy_confdir}/haproxy.cfg
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/haproxy
%{__install} -p -D -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/haproxy
%{__install} -d -m 0755 %{buildroot}%{haproxy_home}
%{__install} -d -m 0755 %{buildroot}%{haproxy_datadir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -p -m 0755 ./contrib/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./contrib/iprange/iprange %{buildroot}%{_bindir}/iprange
%{__install} -p -m 0644 ./examples/errorfiles/* %{buildroot}%{haproxy_datadir}

for file in $(find . -type f -name '*.txt') ; do
    iconv -f ISO-8859-1 -t UTF-8 -o $file.new $file && \
    touch -r $file $file.new && \
    mv $file.new $file
done

%clean
rm -rf %{buildroot}

%pre
getent group %{haproxy_group} >/dev/null || \
  groupadd -g %{haproxy_gid} -r %{haproxy_group}
getent passwd %{haproxy_user} >/dev/null || \
  useradd -u %{haproxy_uid} -r -g %{haproxy_group} -d %{haproxy_home} \
  -s /sbin/nologin -c "haproxy" %{haproxy_user}
exit 0

%post
%systemd_post haproxy.service

%preun
%systemd_preun haproxy.service

%postun
%systemd_postun_with_restart haproxy.service

%files
%defattr(-,root,root,-)
%doc CHANGELOG LICENSE README ROADMAP VERSION
%doc doc/* examples/*.cfg
%dir %{haproxy_datadir}
%dir %{haproxy_confdir}
%{haproxy_datadir}/*
%config(noreplace) %{haproxy_confdir}/haproxy.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/haproxy
%config(noreplace) %{_sysconfdir}/sysconfig/haproxy
%{_unitdir}/haproxy.service
%{_sbindir}/haproxy
%{_sbindir}/haproxy-systemd-wrapper
%{_bindir}/halog
%{_bindir}/iprange
%{_mandir}/man1/*
%attr(-,%{haproxy_user},%{haproxy_group}) %dir %{haproxy_home}

%changelog
* Fri Jul 21 2017 James Sumners <james.sumners@gmail.com> - 1.7.8
- Update to haproxy 1.7.8
