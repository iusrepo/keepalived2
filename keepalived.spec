%bcond_without snmp
%bcond_without vrrp
%bcond_with profile
%bcond_with debug

%global _hardened_build 1

Name: keepalived
Summary: High Availability monitor built upon LVS, VRRP and service pollers
Version: 1.2.7
Release: 8%{?dist}
License: GPLv2+
URL: http://www.keepalived.org/
Group: System Environment/Daemons

Source0: http://www.keepalived.org/software/keepalived-%{version}.tar.gz
Source1: keepalived.service

Patch0: keepalived-1.2.7-dont-respawn-children.patch
Patch1: keepalived-1.2.7-cleanup-duplicate-option-code.patch
Patch2: keepalived-1.2.7-generate-usage-message-from-popt.patch
Patch3: keepalived-1.2.7-update-keepalived-man-page.patch
Patch4: keepalived-1.2.7-fix-pointer-arithmetic-vrrp-packet.patch
Patch8: keepalived-1.2.7-fix-primary-ip-address-comparison.patch
Patch5: keepalived-1.2.7-fix-ssl-certificate-load.patch
Patch6: keepalived-1.2.7-fix-error-message.patch
Patch7: keepalived-1.2.7-update-gpl-license.patch
Patch9: keepalived-1.2.7-remove-debug-messages.patch
Patch10: keepalived-1.2.7-fix-man-page-macro.patch

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%if %{with snmp}
BuildRequires: net-snmp-devel
%endif
BuildRequires: systemd-units
BuildRequires: openssl-devel
BuildRequires: libnl-devel
BuildRequires: kernel-devel
BuildRequires: popt-devel

%description
Keepalived provides simple and robust facilities for load balancing
and high availability to Linux system and Linux based infrastructures.
The load balancing framework relies on well-known and widely used
Linux Virtual Server (IPVS) kernel module providing Layer4 load
balancing. Keepalived implements a set of checkers to dynamically and
adaptively maintain and manage load-balanced server pool according
their health. High availability is achieved by VRRP protocol. VRRP is
a fundamental brick for router failover. In addition, keepalived
implements a set of hooks to the VRRP finite state machine providing
low-level and high-speed protocol interactions. Keepalived frameworks
can be used independently or all together to provide resilient
infrastructures.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1

%build
%configure \
    %{?with_debug:--enable-debug} \
    %{?with_profile:--enable-profile} \
    %{!?with_vrrp:--disable-vrrp} \
    %{?with_snmp:--enable-snmp}
%{__make} %{?_smp_mflags} STRIP=/bin/true

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
rm -rf %{buildroot}%{_initrddir}/
rm -rf %{buildroot}%{_sysconfdir}/keepalived/samples/
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/keepalived.service

%if %{with snmp}
mkdir -p %{buildroot}%{_datadir}/snmp/mibs/
%{__install} -p -D -m 0644 doc/KEEPALIVED-MIB %{buildroot}%{_datadir}/snmp/mibs/KEEPALIVED-MIB.txt
%endif

%clean
rm -rf %{buildroot}

%post
%systemd_post keepalived.service

%preun
%systemd_preun keepalived.service

%postun
%systemd_postun_with_restart keepalived.service

%files
%defattr(-,root,root,-)
%attr(0755,root,root) %{_sbindir}/keepalived
%attr(0644,root,root) %{_sysconfdir}/sysconfig/keepalived
%attr(0644,root,root) %{_sysconfdir}/keepalived/keepalived.conf
%doc AUTHOR ChangeLog CONTRIBUTORS COPYING README TODO
%doc doc/keepalived.conf.SYNOPSIS doc/samples/keepalived.conf.*
%dir %{_sysconfdir}/keepalived/
%config(noreplace) %{_sysconfdir}/keepalived/keepalived.conf
%config(noreplace) %{_sysconfdir}/sysconfig/keepalived
%if %{with snmp}
%{_datadir}/snmp/mibs/KEEPALIVED-MIB.txt
%endif
%{_bindir}/genhash
%{_unitdir}/keepalived.service
%{_sbindir}/keepalived
%{_mandir}/man1/genhash.1*
%{_mandir}/man5/keepalived.conf.5*
%{_mandir}/man8/keepalived.8*

%changelog
* Mon Jul 22 2013 Ryan O'Hara <rohara@redhat.com> - 1.2.7-8
- Fix macro in keepalived.conf.5 man page.

* Mon Jul 22 2013 Ryan O'Hara <rohara@redhat.com> - 1.2.7-7
- Fix systemd requirements.

* Mon Jul 22 2013 Ryan O'Hara <rohara@redhat.com> - 1.2.7-6
- Install the systemd unit file, not the init script.

* Mon Apr 22 2013 Ryan O'Hara <rohara@redhat.com> - 1.2.7-5
- Build with PIE flags (#955150)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.7-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan 2 2013 Ryan O'Hara <rohara@redhat.com> - 1.2.7-3
- Update spec file.
- Add option to prevent respawn of child processes.
- Remove duplicate command-line option code.
- Use popt to generate usage message.
- Fix pointer arithmetic for VRRP packets.
- Fix comparison of primary IP address.
- Fix loading of SSL certificate.
- Fix typo in error message.
- Update FSF address in GPLv2 license.
- Remove debug message from if_get_by_ifname.

* Mon Sep 24 2012 Václav Pavlín <vpavlin@redhat.com> - 1.2.7-2
- Scriptlets replaced with new systemd macros (#850173).

* Tue Sep 04 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.7-1
- Update to 1.2.7.
- Fix systemd service file (#769726).

* Mon Aug 20 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.6-1
- Update to 1.2.6.

* Tue Aug 14 2012 Ryan O'Hara <rohara@redhat.com> - 1.2.5-2
- Install KEEPALIVED-MIB as KEEPALIVED-MIB.txt.

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

