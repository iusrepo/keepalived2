Summary: High Availability monitor built upon LVS, VRRP and service pollers
Name: keepalived
Version: 1.2.7
Release: 1%{?dist}
License: GPLv2+
Group: Applications/System
URL: http://www.keepalived.org/
Source0: http://www.keepalived.org/software/keepalived-%{version}.tar.gz
Source1: keepalived.service
Patch0: keepalived-1.1.14-installmodes.patch
Requires(post): systemd-sysv
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
BuildRequires: systemd-units
BuildRequires: openssl-devel
%if 0%{?fedora:1} || 0%{?rhel} >= 6
BuildRequires: libnl-devel
%else
# The RHEL <= 5 libnl is too old for the compilation to work
BuildConflicts: libnl-devel < 1.1
%endif
# We need both of these for proper LVS support
BuildRequires: kernel, kernel-devel, kernel-headers
# We need popt, popt-devel is split out of rpm in Fedora 8+ and RHEL 6+
%if 0%{?fedora} >= 8 || 0%{?rhel} >= 6
BuildRequires: popt-devel
%endif
# We need net-snmp-devel for SNMP support
BuildRequires: net-snmp-devel
# can't be built on platforms where we don't provide 32-bit kernel
ExcludeArch: s390 sparc sparcv9

%description
The main goal of the keepalived project is to add a strong & robust keepalive
facility to the Linux Virtual Server project. This project is written in C with
multilayer TCP/IP stack checks. Keepalived implements a framework based on
three family checks : Layer3, Layer4 & Layer5/7. This framework gives the
daemon the ability to check the state of an LVS server pool. When one of the
servers of the LVS server pool is down, keepalived informs the linux kernel via
a setsockopt call to remove this server entry from the LVS topology. In
addition keepalived implements an independent VRRPv2 stack to handle director
failover. So in short keepalived is a userspace daemon for LVS cluster nodes
healthchecks and LVS directors failover.


%prep
%setup -q
%patch0 -p1 -b .installmodes


%build
# Get the most recent available kernel build dir, allows to expand arch too
KERNELDIR=$(ls -1d --sort t /lib/modules/*/build | head -1)
%configure --with-kernel-dir="${KERNELDIR}" --enable-snmp
%{__make} %{?_smp_mflags} STRIP=/bin/true


%install
%{__make} install DESTDIR=%{buildroot}
# Remove "samples", as we include them in %%doc
%{__rm} -rf %{buildroot}%{_sysconfdir}/keepalived/samples/
rm -rf %{buildroot}%{_sysconfdir}/rc.d/init.d/
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_datadir}/snmp/mibs
%{__install} -p -m 0755 %{SOURCE1} \
    %{buildroot}%{_unitdir}/keepalived.service
%{__install} -p -m 0644 doc/KEEPALIVED-MIB \
    %{buildroot}%{_datadir}/snmp/mibs/KEEPALIVED-MIB.txt


%check
# A build could silently have LVS support disabled if the kernel includes can't
# be properly found, we need to avoid that.
if ! grep -q "IPVS_SUPPORT='_WITH_LVS_'" config.log; then
    echo "ERROR: We do not want keeepalived lacking LVS support."
    exit 1
fi

%post
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable keepalived.service > /dev/null 2>&1 || :
    /bin/systemctl stop keepalived.service > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart keepalived.service >/dev/null 2>&1 || :
fi

%triggerun -- keepalived < 1.2.2-3
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply keepalived
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save keepalived >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del keepalived >/dev/null 2>&1 || :
/bin/systemctl try-restart keepalived.service >/dev/null 2>&1 || :

%files
%doc AUTHOR ChangeLog CONTRIBUTORS COPYING README TODO
%doc doc/keepalived.conf.SYNOPSIS doc/samples/
%dir %{_sysconfdir}/keepalived/
%config(noreplace) %{_sysconfdir}/keepalived/keepalived.conf
%config(noreplace) %{_sysconfdir}/sysconfig/keepalived
%{_unitdir}/keepalived.service
%{_datadir}/snmp/mibs/KEEPALIVED-MIB.txt
%{_bindir}/genhash
%{_sbindir}/keepalived
%{_mandir}/man1/genhash.1*
%{_mandir}/man5/keepalived.conf.5*
%{_mandir}/man8/keepalived.8*


%changelog
* Tue Sep 04 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.7-1
- Update to 1.2.7.
- Fix systemd service file (#769726).

* Mon Aug 20 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.6-1
- Update to 1.2.6.

* Tue Aug 14 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.5-2
- Install KEEPALIVED-MIB as KEEPALIVED-MIB.txt

* Mon Aug 13 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.5-1
- Update to 1.2.5.

* Wed Aug 01 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.4-1
- Update to 1.2.4.

* Mon Jul 23 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.3-1
- Update to 1.2.3.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue May 08 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.2-5
- Fix IPv4 address comparison (#768119).

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Sep 19 2011 Tom Callaway <spot@fedoraproject.org> - 1.2.2-3
- convert to systemd
- fix ip_vs.h path searching in configure

* Tue Jul 23 2011 Matthias Saou <http://freshrpms.net/> 1.2.2-2
- Build against libnl for Fedora. RHEL's libnl is too old.

* Sat May 21 2011 Matthias Saou <http://freshrpms.net/> 1.2.2-1
- Update to 1.2.2.

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.20-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Jan 16 2011 Dan Horák <dan[at]danny.cz> 1.1.20-2
- exclude arches where we don't provide 32-bit kernel

* Tue Jan 11 2011 Matthias Saou <http://freshrpms.net/> 1.2.1-1
- Update to 1.2.1, now with IPv6 support.

* Sun May 23 2010 Matthias Saou <http://freshrpms.net/> 1.1.20-1
- Update to 1.1.20 (#589923).
- Update BR conditional for RHEL6.
- No longer include goodies/arpreset.pl, it's gone from the sources.

* Tue Dec  8 2009 Matthias Saou <http://freshrpms.net/> 1.1.19-3
- Update init script to have keepalived start after the local MTA (#526512).
- Simplify the kernel source detection, to avoid running rpm from rpmbuild.

* Tue Nov 24 2009 Matthias Saou <http://freshrpms.net/> 1.1.19-2
- Include patch to remove obsolete -k option to modprobe (#528465).

* Wed Oct 21 2009 Matthias Saou <http://freshrpms.net/> 1.1.19-1
- Update to 1.1.19.

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.1.17-3
- rebuilt with new openssl

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.17-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Apr 12 2009 Matthias Saou <http://freshrpms.net/> 1.1.17-1
- Update to 1.1.17.
- Update init script all the way.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> 1.1.15-7
- rebuild with new openssl

* Mon Dec 22 2008 Matthias Saou <http://freshrpms.net/> 1.1.15-6
- Fork the init script to be (mostly for now) LSB compliant (#246966).

* Thu Apr 24 2008 Matthias Saou <http://freshrpms.net/> 1.1.15-5
- Add glob to the kerneldir location, since it contains the arch for F9+.

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org>
- Autorebuild for GCC 4.3

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org>
- Rebuild for deps

* Mon Oct 22 2007 Matthias Saou <http://freshrpms.net/> 1.1.15-2
- Update to latest upstream sources, identical except for the included spec.

* Mon Sep 17 2007 Matthias Saou <http://freshrpms.net/> 1.1.15-1
- Update to 1.1.15.
- Remove merged genhashman and include patches.

* Fri Sep 14 2007 Matthias Saou <http://freshrpms.net/> 1.1.14-2
- Include patch from Shinji Tanaka to fix conf include from inside some
  directives like vrrp_instance.

* Thu Sep 13 2007 Matthias Saou <http://freshrpms.net/> 1.1.14-1
- Update to 1.1.14.
- Remove all upstreamed patches.
- Remove our init script and sysconfig files, use the same now provided by the
  upstream package (will need to patch for LSB stuff soonish).
- Include new goodies/arpreset.pl in %%doc.
- Add missing scriplet requirements.

* Wed Aug 22 2007 Matthias Saou <http://freshrpms.net/> 1.1.13-8
- Rebuild for new BuildID feature.

* Sun Aug  5 2007 Matthias Saou <http://freshrpms.net/> 1.1.13-7
- Update License field.

* Mon Mar 26 2007 Matthias Saou <http://freshrpms.net/> 1.1.13-6
- Fix doc/samples/sample.misccheck.smbcheck.sh mode (600 -> 644).

* Thu Mar 22 2007 Matthias Saou <http://freshrpms.net/> 1.1.13-5
- Include types patch to fix compile on F7 (David Woodhouse).
- Fix up file modes (main binary 700 -> 755 and config 600 -> 640).

* Tue Feb 13 2007 Matthias Saou <http://freshrpms.net/> 1.1.13-4
- Add missing \n to the kernel define, for when multiple kernels are installed.
- Pass STRIP=/bin/true to "make" in order to get a useful debuginfo package.

* Tue Feb 13 2007 Matthias Saou <http://freshrpms.net/> 1.1.13-3
- Add %%check section to make sure any build without LVS support will fail.

* Mon Feb  5 2007 Matthias Saou <http://freshrpms.net/> 1.1.13-2
- Use our own init script, include a sysconfig entry used by it for options.

* Thu Jan 25 2007 Matthias Saou <http://freshrpms.net/> 1.1.13-1
- Update to 1.1.13.
- Change mode of configuration file to 0600.
- Don't include all of "doc" since it meant re-including all man pages.
- Don't include samples in the main configuration path, they're in %%doc.
- Include patch to add an optional label to interfaces.

* Sat Apr 08 2006 Dries Verachtert <dries@ulyssis.org> - 1.1.12-1.2
- Rebuild for Fedora Core 5.

* Sun Mar 12 2006 Dag Wieers <dag@wieers.com> - 1.1.12-1
- Updated to release 1.1.12.

* Fri Mar 04 2005 Dag Wieers <dag@wieers.com> - 1.1.11-1
- Updated to release 1.1.11.

* Wed Feb 23 2005 Dag Wieers <dag@wieers.com> - 1.1.10-2
- Fixed IPVS/LVS support. (Joe Sauer)

* Tue Feb 15 2005 Dag Wieers <dag@wieers.com> - 1.1.10-1
- Updated to release 1.1.10.

* Mon Feb 07 2005 Dag Wieers <dag@wieers.com> - 1.1.9-1
- Updated to release 1.1.9.

* Sun Oct 17 2004 Dag Wieers <dag@wieers.com> - 1.1.7-2
- Fixes to build with kernel IPVS support. (Tim Verhoeven)

* Fri Sep 24 2004 Dag Wieers <dag@wieers.com> - 1.1.7-1
- Updated to release 1.1.7. (Mathieu Lubrano)

* Mon Feb 23 2004 Dag Wieers <dag@wieers.com> - 1.1.6-0
- Updated to release 1.1.6.

* Mon Jan 26 2004 Dag Wieers <dag@wieers.com> - 1.1.5-0
- Updated to release 1.1.5.

* Mon Dec 29 2003 Dag Wieers <dag@wieers.com> - 1.1.4-0
- Updated to release 1.1.4.

* Fri Jun 06 2003 Dag Wieers <dag@wieers.com> - 1.0.3-0
- Initial package. (using DAR)

