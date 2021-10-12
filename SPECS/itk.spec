# Namespace
%global ns_name ea-apache24
%global module_name mpm_itk

%global vnum 2.4.7
# pnumtar is the patch release assigned by author (since author uses filename to assign revisions)
# so, if you update pnumtar, you must update pnum so it can be used in the version we use in this package
%global pnumtar 04
%global pnum 4
%global itk_version %{vnum}.%{pnum}

Summary: Run all httpd process under user's access rights.
Name: %{ns_name}-mod_%{module_name}
# This needs to be one var in order for `et` to parse it correctly
Version: %{itk_version}
Vendor: cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4564 for more details
%define release_prefix 4
Release: %{release_prefix}%{?dist}.cpanel
Group: System Environment/Daemons
URL: http://mpm-itk.sesse.net/
Source0: http://mpm-itk.sesse.net/mpm-itk-%{vnum}-%{pnumtar}.tar.gz
Source1: http://www.apache.org/licenses/LICENSE-2.0.txt
License: Apache Software License version 2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: %{ns_name}-devel >= 2.4.0 libcap-devel
BuildRequires: libtool
# NOTE: These 2 BuildRequires statements are needed because of a decision
# we made in EA4 to allow the user to pick and choose which mpm to work
# with.  Unfortunately, this prevents YUM from solving dependencies
# because it doesn't know which package to use.  This tells YUM which
# to use so it can build this MPM.  We may need to revert this opinion
# in the future.
#BuildRequires: ea-mod_mpm_prefork
#BuildRequires: ea-mod_cgi
Requires: %{ns_name}-mpm = forked
Requires: %{ns_name}-mmn = %{_httpd_mmn}
Requires: libcap
Conflicts: %{ns_name}-mod_ruid2 %{ns_name}-mod_suexec %{ns_name}-mod_suphp %{ns_name}-mod_mpm_event %{ns_name}-mod_mpm_worker
Conflicts: %{ns_name}-mod_fcgid
Conflicts: %{ns_name}-mod_http2
Provides: %{ns_name}-exec_code_asuser
Patch0: 0001-min_uid.patch
Patch1: 0002-Avoid-segfault-when-socket-connection-is-null.patch

%description
This module allows you to run each virtual host as a separate uid/gid.  It depends on
the (non-thread) prefork MPM.  There are considerable security, speed, and memory
trade-offs to consider when using this module.  You should profile your web server
in a test environment to ensure that these trade-offs are sufficient in your
environment.

%prep
: Building %{name} %{version}-%{release} %{_arch} %{ns_name}-mmn = %{_httpd_mmn}
%setup -q -n mpm-itk-%{vnum}-%{pnumtar}
%{__cp} %{SOURCE1} .
%patch0 -p1 -b .minuid
%patch1 -p1 -b .avoidsegfault

%build
%{configure} --with-apxs=%{_httpd_apxs} && make

%install
%{__rm} -rf %{buildroot}

# install module
%{__mkdir_p} %{buildroot}%{_httpd_moddir}
%{__install} -m0755 .libs/%{module_name}.so %{buildroot}%{_httpd_moddir}/

# install docs
#echo "Installing docs"
#mkdir -p %{buildroot}%{_defaultdocdir}
#install %{SOURCE1} %{buildroot}%{_docdir}
#install README CHANGES %{buildroot}%{_docdir}

# install apache config
%{__mkdir_p} %{buildroot}%{_httpd_modconfdir}
echo "LoadModule %{module_name}_module modules/%{module_name}.so" > %{buildroot}%{_httpd_modconfdir}/900-%{module_name}.conf

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(644,root,root,755)
%doc README CHANGES LICENSE-2.0.txt
%attr(755,root,root)%{_httpd_moddir}/*.so
%config(noreplace) %{_httpd_modconfdir}/*.conf


%changelog
* Thu Sep 30 2021 Travis Holloway <t.holloway@cpanel.net> - 2.4.7.4-4
- EA-10143: EA-10143: Patch mpm_itk.c to avoid segfault against apache 2.4.49 and newer

* Wed Nov 15 2017 Cory McIntire <cory@cpanel.net> - 2.4.7.4-3
- EA-6580: patch mpm_itk.c to allow UID/GID changes for sub processes

* Thu Jun 15 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.7.4-2
- EA-6232: Add conflict for mod_http2

* Tue Feb 7 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 2.4.7.4-1
- EA-4714: Update mpm_itk for newest package

* Tue Oct 18 2016 Edwin Buck <e.buck@cpanel.net> - 2.4.7.2-5
- EA-5441: Make mod_fcid and mod_itk conflict with each other.

* Mon Jun 20 2016 Dan Muey <dan@cpanel.net> - 2.4.7.2-4
- EA-4383: Update Release value to OBS-proof versioning

* Mon Oct 19 2015 Darren Mobley <darren@cpanel.net> 2.4.07-02-1
- Added specific conflicts with uncompatible MPMs

* Mon Jun 15 2015 S. Kurt Newman <kurt.newman@cpanel.net> 2.4.07-02-0
- Initial creation
