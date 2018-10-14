%global _hardened_build 1

%global _for_fedora_koji_builds 1

# uncomment and add '%' to use the prereltag for pre-releases
#global prereltag rc0

##-----------------------------------------------------------------------------
## All argument definitions should be placed here and keep them sorted
##

# if you wish to compile an rpm with debugging...
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --with debug
%{?_with_debug:%global _with_debug --enable-debug}

# if you wish to compile an rpm to run all processes under valgrind...
# rpmbuild -ta glusterfs-3.11.0rc0.tar.gz --with valgrind
%{?_with_valgrind:%global _with_valgrind --enable-valgrind}

# if you wish to compile an rpm with cmocka unit testing...
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --with cmocka
%{?_with_cmocka:%global _with_cmocka --enable-cmocka}

# if you wish to compile an rpm without rdma support, compile like this...
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without rdma
%{?_without_rdma:%global _without_rdma --disable-ibverbs}

# No RDMA Support on s390(x)
%ifarch s390 s390x
%global _without_rdma --disable-ibverbs
%endif

# if you wish to compile an rpm without epoll...
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without epoll
%{?_without_epoll:%global _without_epoll --disable-epoll}

# if you wish to compile an rpm without fusermount...
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without fusermount
%{?_without_fusermount:%global _without_fusermount --disable-fusermount}

# if you wish to compile an rpm without geo-replication support, compile like this...
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without georeplication
%{?_without_georeplication:%global _without_georeplication --disable-georeplication}

# Disable geo-replication on EL5, as its default Python is too old
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_georeplication --disable-georeplication
%endif

# enable the glusterfs-gnfs package by default
%global _with_gnfs --enable-gnfs

# if you wish to compile an rpm without the OCF resource agents...
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without ocf
%{?_without_ocf:%global _without_ocf --without-ocf}

# if you wish to build rpms without syslog logging, compile like this
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without syslog
%{?_without_syslog:%global _without_syslog --disable-syslog}

# disable syslog forcefully as rhel <= 6 doesn't have rsyslog or rsyslog-mmcount
# Fedora deprecated syslog, see
#  https://fedoraproject.org/wiki/Changes/NoDefaultSyslog
# (And what about RHEL7?)
%if ( 0%{?fedora} && 0%{?fedora} >= 20 ) || ( 0%{?rhel} && 0%{?rhel} < 7 )
%global _without_syslog --disable-syslog
%endif

# if you wish to compile an rpm without the BD map support...
# rpmbuild -ta @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz --without bd
%{?_without_bd:%global _without_bd --disable-bd-xlator}

%if ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} )
%global _without_bd --disable-bd-xlator
%endif

# Disable data-tiering on EL5, sqlite is too old
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_tiering --disable-tiering
%endif

##-----------------------------------------------------------------------------
## All %%global definitions should be placed here and keep them sorted
##

%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
%global _with_systemd true
%endif

%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
%global _with_firewalld --enable-firewalld
%endif

%if 0%{?_tmpfilesdir:1}
%global _with_tmpfilesdir --with-tmpfilesdir=%{_tmpfilesdir}
%else
%global _with_tmpfilesdir --without-tmpfilesdir
%endif

# Eventing
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%global _without_events --disable-events
%endif

# From https://fedoraproject.org/wiki/Packaging:Python#Macros
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
%{!?python2_sitelib: %global python2_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%if ( 0%{?_with_systemd:1} )
%global service_start()   /bin/systemctl --quiet start %1.service || : \
%{nil}
%global service_stop()    /bin/systemctl --quiet stop %1.service || :\
%{nil}
%global service_install() install -D -p -m 0644 %1.service %{buildroot}%2 \
%{nil}
# can't seem to make a generic macro that works
%global glusterd_svcfile   %{_unitdir}/glusterd.service
%global glusterfsd_svcfile %{_unitdir}/glusterfsd.service
%global glustereventsd_svcfile %{_unitdir}/glustereventsd.service
%global glusterfssharedstorage_svcfile %{_unitdir}/glusterfssharedstorage.service
%else
%global systemd_post()  /sbin/chkconfig --add %1 >/dev/null 2>&1 || : \
%{nil}
%global systemd_preun() /sbin/chkconfig --del %1 >/dev/null 2>&1 || : \
%{nil}
%global systemd_postun_with_restart() /sbin/service %1 condrestart >/dev/null 2>&1 || : \
%{nil}
%global service_start()   /sbin/service %1 start >/dev/null 2>&1 || : \
%{nil}
%global service_stop()    /sbin/service %1 stop >/dev/null 2>&1 || : \
%{nil}
%global service_install() install -D -p -m 0755 %1.init %{buildroot}%2 \
%{nil}
# can't seem to make a generic macro that works
%global glusterd_svcfile   %{_sysconfdir}/init.d/glusterd
%global glusterfsd_svcfile %{_sysconfdir}/init.d/glusterfsd
%global glustereventsd_svcfile %{_sysconfdir}/init.d/glustereventsd
%endif

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

%if ( 0%{?rhel} && 0%{?rhel} < 6 )
# _sharedstatedir is not provided by RHEL5
%global _sharedstatedir /var/lib
%endif

# We do not want to generate useless provides and requires for xlator
# .so files to be set for glusterfs packages.
# Filter all generated:
#
# TODO: RHEL5 does not have a convenient solution
%if ( 0%{?rhel} == 6 )
# filter_setup exists in RHEL6 only
%filter_provides_in %{_libdir}/glusterfs/%{version}/
%global __filter_from_req %{?__filter_from_req} | grep -v -P '^(?!lib).*\.so.*$'
%filter_setup
%else
# modern rpm and current Fedora do not generate requires when the
# provides are filtered
%global __provides_exclude_from ^%{_libdir}/glusterfs/%{version}/.*$
%endif


##-----------------------------------------------------------------------------
## All package definitions should be placed here in alphabetical order
##
Summary:          Distributed File System
%if ( 0%{_for_fedora_koji_builds} )
Name:             glusterfs
Version:          3.12.15
Release:          %{?prereltag:0.}1%{?prereltag:.%{prereltag}}%{?dist}
%else
Name:             @PACKAGE_NAME@
Version:          @PACKAGE_VERSION@
Release:          0.@PACKAGE_RELEASE@%{?dist}.3
%endif
License:          GPLv2 or LGPLv3+
Group:            System Environment/Base
URL:              http://gluster.readthedocs.io/en/latest/
%if ( 0%{_for_fedora_koji_builds} )
Source0:          http://bits.gluster.org/pub/gluster/%{name}/src/%{name}-%{version}%{?prereltag}.tar.gz
Source1:          glusterd.sysconfig
Source2:          glusterfsd.sysconfig
Source6:          rhel5-load-fuse-modules
Source7:          glusterfsd.service
Source8:          glusterfsd.init
%else
Source0:          @PACKAGE_NAME@-@PACKAGE_VERSION@.tar.gz
%endif

BuildRoot:        %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Requires(pre):    shadow-utils
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
BuildRequires:    python-simplejson
%endif
%if ( 0%{?_with_systemd:1} )
BuildRequires:    systemd
%endif

%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?_with_systemd:1} )
%global glusterfsd_service %{S:%{SOURCE7}}
%else
%global glusterfsd_service %{S:%{SOURCE8}}
%endif
%endif

Requires:         %{name}-libs = %{version}-%{release}
%if ( 0%{?_with_systemd:1} )
%{?systemd_requires}
%endif
BuildRequires:    bison flex
BuildRequires:    gcc make libtool
BuildRequires:    ncurses-devel readline-devel
BuildRequires:    libxml2-devel openssl-devel
BuildRequires:    libaio-devel libacl-devel
BuildRequires:    python2-devel
%if ( 0%{?rhel} )
BuildRequires:    python-ctypes
%endif
BuildRequires:    userspace-rcu-devel >= 0.7
%if ( 0%{?rhel} && 0%{?rhel} < 7 )
BuildRequires:    automake
%endif
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
BuildRequires:    e2fsprogs-devel
%else
BuildRequires:    libuuid-devel
%endif
%if ( 0%{?_with_cmocka:1} )
BuildRequires:    libcmocka-devel >= 1.0.1
%endif
%if ( 0%{!?_without_tiering:1} )
BuildRequires:    sqlite-devel
%endif
%if ( 0%{!?_without_bd:1} )
BuildRequires:    lvm2-devel
%endif
%if ( 0%{!?_without_georeplication:1} )
BuildRequires:    libattr-devel
%endif

%if (0%{?_with_firewalld:1})
BuildRequires:    firewalld
%endif

Obsoletes:        hekafs
Obsoletes:        %{name}-common < %{version}-%{release}
Obsoletes:        %{name}-core < %{version}-%{release}
%if ( 0%{_for_fedora_koji_builds} )
Obsoletes:        %{name}-regression-tests
%endif
Obsoletes:        %{name}-ufo
Obsoletes:        %{name}-ganesha
Provides:         %{name}-common = %{version}-%{release}
Provides:         %{name}-core = %{version}-%{release}

%description
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package includes the glusterfs binary, the glusterfsd daemon and the
libglusterfs and glusterfs translator modules common to both GlusterFS server
and client framework.

%package api
Summary:          GlusterFS api library
Group:            System Environment/Daemons
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-client-xlators = %{version}-%{release}

%description api
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the glusterfs libgfapi library.

%package api-devel
Summary:          Development Libraries
Group:            Development/Libraries
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-devel = %{version}-%{release}
Requires:         libacl-devel

%description api-devel
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the api include files.

%package cli
Summary:          GlusterFS CLI
Group:            Applications/File
Requires:         %{name}-libs = %{version}-%{release}

%description cli
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the GlusterFS CLI application and its man page

%package devel
Summary:          Development Libraries
Group:            Development/Libraries
Requires:         %{name} = %{version}-%{release}
# Needed for the Glupy examples to work
Requires:         %{name}-extra-xlators = %{version}-%{release}

%description devel
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the development libraries and include files.

%package extra-xlators
Summary:          Extra Gluster filesystem Translators
Group:            Applications/File
# We need python2-gluster rpm for gluster module's __init__.py in Python
# site-packages area
Requires:         python2-gluster = %{version}-%{release}
Requires:         python2
%if ( 0%{?rhel} )
BuildRequires:    python-ctypes
%endif

%description extra-xlators
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides extra filesystem Translators, such as Glupy,
for GlusterFS.

%package fuse
Summary:          Fuse client
Group:            Applications/File
BuildRequires:    fuse-devel
Requires:         attr
Requires:         psmisc

Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-client-xlators = %{version}-%{release}

Obsoletes:        %{name}-client < %{version}-%{release}
Provides:         %{name}-client = %{version}-%{release}

%description fuse
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides support to FUSE based clients and inlcudes the
glusterfs(d) binary.

%if ( 0%{!?_without_georeplication:1} )
%package geo-replication
Summary:          GlusterFS Geo-replication
Group:            Applications/File
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-server = %{version}-%{release}
Requires:         python2
Requires:         python-prettytable
%if ( 0%{?rhel} )
BuildRequires:    python-ctypes
%endif
Requires:         python2-gluster = %{version}-%{release}
Requires:         rsync

%description geo-replication
GlusterFS is a distributed file-system capable of scaling to several
peta-bytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file system in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in userspace and easily manageable.

This package provides support to geo-replication.
%endif

%if ( 0%{?_with_gnfs:1} )
%package gnfs
Summary:          GlusterFS gNFS server
Group:            System Environment/Daemons
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-client-xlators%{?_isa} = %{version}-%{release}
Requires:         nfs-utils

%description gnfs
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the glusterfs legacy gNFS server xlator
%endif

%package libs
Summary:          GlusterFS common libraries
Group:            Applications/File

%description libs
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the base GlusterFS libraries

%package -n python-gluster
Summary:          GlusterFS python library
Group:            Development/Tools
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} ) )
# EL5 does not support noarch sub-packages
BuildArch:        noarch
%endif

%global _python_gluster_description \
GlusterFS is a distributed file-system capable of scaling to several\
petabytes. It aggregates various storage bricks over Infiniband RDMA\
or TCP/IP interconnect into one large parallel network file\
system. GlusterFS is one of the most sophisticated file systems in\
terms of features and extensibility.  It borrows a powerful concept\
called Translators from GNU Hurd kernel. Much of the code in GlusterFS\
is in user space and easily manageable.\
\
This package contains the python modules of GlusterFS and own gluster\
namespace.

%description -n python-gluster %{_python_gluster_description}

%package -n python2-gluster
Summary:          GlusterFS python library
Group:            Development/Tools
%{?python_provide:%python_provide python2-gluster}
Requires:         python2
Provides:         python-gluster = %{version}-%{release}
Obsoletes:        python-gluster < 3.10

%description -n python2-gluster %{_python_gluster_description}

%if ( 0%{!?_without_rdma:1} )
%package rdma
Summary:          GlusterFS rdma support for ib-verbs
Group:            Applications/File
%if ( 0%{?fedora} && 0%{?fedora} > 26 )
BuildRequires:    rdma-core-devel
%else
BuildRequires:    libibverbs-devel
BuildRequires:    librdmacm-devel >= 1.0.15
%endif
Requires:         %{name} = %{version}-%{release}

%description rdma
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides support to ib-verbs library.
%endif

%if ( ! 0%{_for_fedora_koji_builds} )
%package regression-tests
Summary:          Development Tools
Group:            Development/Tools
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-fuse = %{version}-%{release}
Requires:         %{name}-server = %{version}-%{release}
## thin provisioning support
Requires:         lvm2 >= 2.02.89
Requires:         perl(App::Prove) perl(Test::Harness) gcc util-linux-ng
Requires:         python2 attr dbench file git libacl-devel net-tools
Requires:         nfs-utils xfsprogs yajl psmisc bc

%description regression-tests
The Gluster Test Framework, is a suite of scripts used for
regression testing of Gluster.
%endif

%if ( 0%{!?_without_ocf:1} )
%package resource-agents
Summary:          OCF Resource Agents for GlusterFS
License:          GPLv3+
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 || 0%{?sles_version} ) )
# EL5 does not support noarch sub-packages
BuildArch:        noarch
%endif
# this Group handling comes from the Fedora resource-agents package
%if ( 0%{?fedora} || 0%{?centos_version} || 0%{?rhel} )
Group:            System Environment/Base
%else
Group:            Productivity/Clustering/HA
%endif
# for glusterd
Requires:         %{name}-server = %{version}-%{release}
# depending on the distribution, we need pacemaker or resource-agents
Requires:         %{_prefix}/lib/ocf/resource.d

%description resource-agents
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the resource agents which plug glusterd into
Open Cluster Framework (OCF) compliant cluster resource managers,
like Pacemaker.
%endif

%package server
Summary:          Distributed file-system server
Group:            System Environment/Daemons
Requires:         %{name} = %{version}-%{release}
Requires:         %{name}-libs = %{version}-%{release}
Requires:         %{name}-cli = %{version}-%{release}
# some daemons (like quota) use a fuse-mount, glusterfsd is part of -fuse
Requires:         %{name}-fuse = %{version}-%{release}
# self-heal daemon, rebalance, nfs-server etc. are actually clients
Requires:         %{name}-api = %{version}-%{release}
Requires:         %{name}-client-xlators = %{version}-%{release}
# lvm2 for snapshot, and nfs-utils and rpcbind/portmap for gnfs server
Requires:         lvm2
%if ( 0%{?_with_systemd:1} )
%{?systemd_requires}
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/service
Requires(preun):  /sbin/chkconfig
Requires(postun): /sbin/service
%endif
%if (0%{?_with_firewalld:1})
# we install firewalld rules, so we need to have the directory owned
%if ( 0%{!?rhel} )
# not on RHEL because firewalld-filesystem appeared in 7.3
# when EL7 rpm gets weak dependencies we can add a Suggests:
Requires:         firewalld-filesystem
%endif
%endif
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
Requires:         rpcbind
%else
Requires:         portmap
%endif
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
Obsoletes:        %{name}-geo-replication = %{version}-%{release}
%endif
%if ( 0%{?rhel} && 0%{?rhel} <= 6 )
Requires:         python-argparse
%endif
Requires:         pyxattr
%if (0%{?_with_valgrind:1})
Requires:         valgrind
%endif

%description server
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the glusterfs server daemon.

%package client-xlators
Summary:          GlusterFS client-side translators
Group:            Applications/File

%description client-xlators
GlusterFS is a distributed file-system capable of scaling to several
petabytes. It aggregates various storage bricks over Infiniband RDMA
or TCP/IP interconnect into one large parallel network file
system. GlusterFS is one of the most sophisticated file systems in
terms of features and extensibility.  It borrows a powerful concept
called Translators from GNU Hurd kernel. Much of the code in GlusterFS
is in user space and easily manageable.

This package provides the translators needed on any GlusterFS client.

%if ( 0%{!?_without_events:1} )
%package events
Summary:          GlusterFS Events
Group:            Applications/File
Requires:         %{name}-server%{?_isa} = %{version}-%{release}
Requires:         python2 python-prettytable
Requires:         python2-gluster = %{version}-%{release}
%if ( 0%{?rhel} )
Requires:         python-requests
%else
Requires:         python2-requests
%endif
%if ( 0%{?rhel} && 0%{?rhel} < 7 )
Requires:         python-argparse
%endif
%if ( 0%{?_with_systemd:1} )
%{?systemd_requires}
%endif

%description events
GlusterFS Events

%endif

%prep
%setup -q -n %{name}-%{version}%{?prereltag}

%build
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
CFLAGS=-DUSE_INSECURE_OPENSSL
export CFLAGS
%endif

./autogen.sh && %configure \
        %{?_with_cmocka} \
        %{?_with_debug} \
        %{?_with_firewalld} \
        %{?_with_gnfs} \
        %{?_with_tmpfilesdir} \
        %{?_with_valgrind} \
        %{?_without_bd} \
        %{?_without_epoll} \
        %{?_without_events} \
        %{?_without_fusermount} \
        %{?_without_georeplication} \
        %{?_without_ocf} \
        %{?_without_rdma} \
        %{?_without_syslog} \
        %{?_without_tiering}

# fix hardening and remove rpath in shlibs
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
sed -i 's| \\\$compiler_flags |&\\\$LDFLAGS |' libtool
%endif
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|' libtool

make %{?_smp_mflags}

%check
make check

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
# Install include directory
install -p -m 0644 contrib/uuid/*.h \
    %{buildroot}%{_includedir}/glusterfs/
%if ( 0%{_for_fedora_koji_builds} )
install -D -p -m 0644 %{SOURCE1} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
install -D -p -m 0644 %{SOURCE2} \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterfsd
%else
install -D -p -m 0644 extras/glusterd-sysconfig \
    %{buildroot}%{_sysconfdir}/sysconfig/glusterd
%endif

%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
install -D -p -m 0755 %{SOURCE6} \
    %{buildroot}%{_sysconfdir}/sysconfig/modules/glusterfs-fuse.modules
%endif
%endif

mkdir -p %{buildroot}%{_localstatedir}/log/glusterd
mkdir -p %{buildroot}%{_localstatedir}/log/glusterfs
mkdir -p %{buildroot}%{_localstatedir}/log/glusterfsd
mkdir -p %{buildroot}%{_rundir}/gluster

# Remove unwanted files from all the shared libraries
find %{buildroot}%{_libdir} -name '*.a' -delete
find %{buildroot}%{_libdir} -name '*.la' -delete

# Remove installed docs, the ones we want are included by %%doc, in
# /usr/share/doc/glusterfs or /usr/share/doc/glusterfs-x.y.z depending
# on the distribution
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} > 6 )
rm -rf %{buildroot}%{_pkgdocdir}/*
%else
rm -rf %{buildroot}%{_defaultdocdir}/%{name}
mkdir -p %{buildroot}%{_pkgdocdir}
%endif
head -50 ChangeLog > ChangeLog.head && mv ChangeLog.head ChangeLog
cat << EOM >> ChangeLog

More commit messages for this ChangeLog can be found at
https://forge.gluster.org/glusterfs-core/glusterfs/commits/v%{version}%{?prereltag}
EOM

# Remove benchmarking and other unpackaged files
%if ( 0%{?rhel} && 0%{?rhel} < 6 )
rm -rf %{buildroot}/benchmarking
rm -f %{buildroot}/glusterfs-mode.el
rm -f %{buildroot}/glusterfs.vim
%else
# make install always puts these in %%{_defaultdocdir}/%%{name} so don't
# use %%{_pkgdocdir}; that will be wrong on later Fedora distributions
rm -rf %{buildroot}%{_defaultdocdir}/%{name}/benchmarking
rm -f %{buildroot}%{_defaultdocdir}/%{name}/glusterfs-mode.el
rm -f %{buildroot}%{_defaultdocdir}/%{name}/glusterfs.vim
%endif

# Create working directory
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd

# Update configuration file to /var/lib working directory
sed -i 's|option working-directory /etc/glusterd|option working-directory %{_sharedstatedir}/glusterd|g' \
    %{buildroot}%{_sysconfdir}/glusterfs/glusterd.vol

# Install glusterfsd .service or init.d file
%if ( 0%{_for_fedora_koji_builds} )
%service_install %{_sourcedir}/glusterfsd %{glusterfsd_svcfile}
%endif

install -D -p -m 0644 extras/glusterfs-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs

%if ( 0%{!?_without_georeplication:1} )
# geo-rep ghosts
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/geo-replication
touch %{buildroot}%{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
install -D -p -m 0644 extras/glusterfs-georep-logrotate \
    %{buildroot}%{_sysconfdir}/logrotate.d/glusterfs-georep
%endif

# the rest of the ghosts
touch %{buildroot}%{_sharedstatedir}/glusterd/glusterd.info
touch %{buildroot}%{_sharedstatedir}/glusterd/options
subdirs=(add-brick create copy-file delete gsync-create remove-brick reset set start stop)
for dir in ${subdirs[@]}; do
    mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/hooks/1/"$dir"/{pre,post}
done
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/glustershd
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/peers
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/vols
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/nfs/run
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/bitd
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/quotad
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/scrub
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/snaps
mkdir -p %{buildroot}%{_sharedstatedir}/glusterd/ss_brick
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/nfs-server.vol
touch %{buildroot}%{_sharedstatedir}/glusterd/nfs/run/nfs.pid

%if ( ! 0%{_for_fedora_koji_builds} )
find ./tests ./run-tests.sh -type f | cpio -pd %{buildroot}%{_prefix}/share/glusterfs
%endif

## Install bash completion for cli
install -p -m 0744 -D extras/command-completion/gluster.bash \
    %{buildroot}%{_sysconfdir}/bash_completion.d/gluster

%clean
rm -rf %{buildroot}

##-----------------------------------------------------------------------------
## All %%post should be placed here and keep them sorted
##
%post
/sbin/ldconfig
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%systemd_postun_with_restart rsyslog
%endif
%endif
exit 0

%post api
/sbin/ldconfig

%if ( 0%{!?_without_events:1} )
%post events
%systemd_post glustereventsd
%endif

%if ( 0%{?rhel} == 5 )
%post fuse
modprobe fuse
exit 0
%endif

%if ( 0%{!?_without_georeplication:1} )
%post geo-replication
if [ $1 -ge 1 ]; then
    %systemd_postun_with_restart glusterd
fi
exit 0
%endif

%post libs
/sbin/ldconfig

%post server
# Legacy server
%systemd_post glusterd
%if ( 0%{_for_fedora_koji_builds} )
%systemd_post glusterfsd
%endif
# ".cmd_log_history" is renamed to "cmd_history.log" in GlusterFS-3.7 .
# While upgrading glusterfs-server package form GlusterFS version <= 3.6 to
# GlusterFS version 3.7, ".cmd_log_history" should be renamed to
# "cmd_history.log" to retain cli command history contents.
if [ -f %{_localstatedir}/log/glusterfs/.cmd_log_history ]; then
    mv %{_localstatedir}/log/glusterfs/.cmd_log_history \
       %{_localstatedir}/log/glusterfs/cmd_history.log
fi

# Genuine Fedora (and EPEL) builds never put gluster files in /etc; if
# there are any files in /etc from a prior gluster.org install, move them
# to /var/lib. (N.B. Starting with 3.3.0 all gluster files are in /var/lib
# in gluster.org RPMs.) Be careful to copy them on the off chance that
# /etc and /var/lib are on separate file systems
if [ -d /etc/glusterd -a ! -h %{_sharedstatedir}/glusterd ]; then
    mkdir -p %{_sharedstatedir}/glusterd
    cp -a /etc/glusterd %{_sharedstatedir}/glusterd
    rm -rf /etc/glusterd
    ln -sf %{_sharedstatedir}/glusterd /etc/glusterd
fi

# Rename old volfiles in an RPM-standard way.  These aren't actually
# considered package config files, so %%config doesn't work for them.
if [ -d %{_sharedstatedir}/glusterd/vols ]; then
    for file in $(find %{_sharedstatedir}/glusterd/vols -name '*.vol'); do
        newfile=${file}.rpmsave
        echo "warning: ${file} saved as ${newfile}"
        cp ${file} ${newfile}
    done
fi

# add marker translator
# but first make certain that there are no old libs around to bite us
# BZ 834847
if [ -e /etc/ld.so.conf.d/glusterfs.conf ]; then
    rm -f /etc/ld.so.conf.d/glusterfs.conf
    /sbin/ldconfig
fi

%if (0%{?_with_firewalld:1})
    %firewalld_reload
%endif

pidof -c -o %PPID -x glusterd &> /dev/null
if [ $? -eq 0 ]; then
    kill -9 `pgrep -f gsyncd.py` &> /dev/null

    killall --wait glusterd &> /dev/null
    glusterd --xlator-option *.upgrade=on -N

    #Cleaning leftover glusterd socket file which is created by glusterd in
    #rpm_script_t context.
    rm -f %{_rundir}/glusterd.socket

    # glusterd _was_ running, we killed it, it exited after *.upgrade=on,
    # so start it again
    %service_start glusterd
else
    glusterd --xlator-option *.upgrade=on -N

    #Cleaning leftover glusterd socket file which is created by glusterd in
    #rpm_script_t context.
    rm -f %{_rundir}/glusterd.socket
fi
exit 0

##-----------------------------------------------------------------------------
## All %%pre should be placed here and keep them sorted
##
%pre
getent group gluster > /dev/null || groupadd -r gluster
getent passwd gluster > /dev/null || useradd -r -g gluster -d %{_rundir}/gluster -s /sbin/nologin -c "GlusterFS daemons" gluster
exit 0


##-----------------------------------------------------------------------------
## All %%preun should be placed here and keep them sorted
##
%if ( 0%{!?_without_events:1} )
%preun events
if [ $1 -eq 0 ]; then
    if [ -f %glustereventsd_svcfile ]; then
        %service_stop glustereventsd
        %systemd_preun glustereventsd
    fi
fi
exit 0
%endif

%preun server
if [ $1 -eq 0 ]; then
    if [ -f %glusterfsd_svcfile ]; then
        %service_stop glusterfsd
    fi
    %service_stop glusterd
    if [ -f %glusterfsd_svcfile ]; then
        %systemd_preun glusterfsd
    fi
    %systemd_postun_with_restart glusterd
fi
if [ $1 -ge 1 ]; then
    if [ -f %glusterfsd_svcfile ]; then
        %systemd_postun_with_restart glusterfsd
    fi
    %systemd_postun_with_restart glusterd
fi
exit 0

##-----------------------------------------------------------------------------
## All %%postun should be placed here and keep them sorted
##
%postun
/sbin/ldconfig
%if ( 0%{!?_without_syslog:1} )
%if ( 0%{?fedora} ) || ( 0%{?rhel} && 0%{?rhel} >= 6 )
%systemd_postun_with_restart rsyslog
%endif
%endif

%postun api
/sbin/ldconfig

%postun libs
/sbin/ldconfig

%postun server
/sbin/ldconfig
%if (0%{?_with_firewalld:1})
    %firewalld_reload
%endif
exit 0

##-----------------------------------------------------------------------------
## All %%files should be placed here and keep them grouped
##
%files
%{!?_licensedir:%global license %%doc}
%license COPYING-GPLV2 COPYING-LGPLV3
%doc ChangeLog INSTALL README.md THANKS
%{_mandir}/man8/*gluster*.8*
%exclude %{_mandir}/man8/gluster.8*
%dir %{_localstatedir}/log/glusterfs
%if ( 0%{!?_without_rdma:1} )
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif
%dir %{_datadir}/glusterfs
%dir %{_datadir}/glusterfs/scripts
     %{_datadir}/glusterfs/scripts/post-upgrade-script-for-quota.sh
     %{_datadir}/glusterfs/scripts/pre-upgrade-script-for-quota.sh
# xlators that are needed on the client- and on the server-side
%dir %{_libdir}/glusterfs
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/auth
     %{_libdir}/glusterfs/%{version}%{?prereltag}/auth/addr.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/auth/login.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport
     %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/socket.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/error-gen.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/io-stats.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/sink.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/debug/trace.so
%if ( ! ( 0%{?rhel} && 0%{?rhel} < 6 ) )
# RHEL-5 based distributions have a too old openssl
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/crypt.so
%endif
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/access-control.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/barrier.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/cdc.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/changelog.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/gfid-access.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/read-only.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/shard.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/snapview-client.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/worm.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/meta.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/io-cache.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/io-threads.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/md-cache.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/open-behind.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/quick-read.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/read-ahead.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/readdir-ahead.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/stat-prefetch.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/write-behind.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/nl-cache.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/system
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/system/posix-acl.so
%dir %attr(0775,gluster,gluster) %{_rundir}/gluster
%if 0%{?_tmpfilesdir:1}
%{_tmpfilesdir}/gluster.conf
%endif

%files api
%exclude %{_libdir}/*.so
# libgfapi files
%{_libdir}/libgfapi.*
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/api.so

%files api-devel
%{_libdir}/pkgconfig/glusterfs-api.pc
%{_libdir}/libgfapi.so
%dir %{_includedir}/glusterfs
%dir %{_includedir}/glusterfs/api
     %{_includedir}/glusterfs/api/*

%files cli
%{_sbindir}/gluster
%{_mandir}/man8/gluster.8*
%{_sysconfdir}/bash_completion.d/gluster

%files devel
%dir %{_includedir}/glusterfs
     %{_includedir}/glusterfs/*
%exclude %{_includedir}/glusterfs/api
%exclude %{_libdir}/libgfapi.so
%{_libdir}/*.so
# Glupy Translator examples
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/debug-trace.*
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/helloworld.*
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy/negative.*
%{_libdir}/pkgconfig/libgfchangelog.pc
%if ( 0%{!?_without_tiering:1} )
%{_libdir}/pkgconfig/libgfdb.pc
%endif

%files client-xlators
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/cluster
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/cluster/*.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/client.so

%files extra-xlators
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/encryption/rot-13.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/glupy.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quiesce.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/features
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/features/template.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/performance
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/testing/performance/symlink-cache.so
# Glupy Python files
%dir %{python2_sitelib}/gluster
%dir %{python2_sitelib}/gluster/glupy
     %{python2_sitelib}/gluster/glupy/*

%files fuse
# glusterfs is a symlink to glusterfsd, -server depends on -fuse.
%{_sbindir}/glusterfs
%{_sbindir}/glusterfsd
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfs
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mount/fuse.so
/sbin/mount.glusterfs
%if ( 0%{!?_without_fusermount:1} )
%{_bindir}/fusermount-glusterfs
%endif
%if ( 0%{_for_fedora_koji_builds} )
%if ( 0%{?rhel} && 0%{?rhel} <= 5 )
%{_sysconfdir}/sysconfig/modules/glusterfs-fuse.modules
%endif
%endif

%if ( 0%{?_with_gnfs:1} )
%files gnfs
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs/server.so
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/nfs
%ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/nfs-server.vol
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/nfs/run
%ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/nfs/run/nfs.pid
%endif

%if ( 0%{!?_without_georeplication:1} )
%files geo-replication
%config(noreplace) %{_sysconfdir}/logrotate.d/glusterfs-georep

%{_sbindir}/gfind_missing_files
%{_sbindir}/gluster-mountbroker
%dir %{_libexecdir}/glusterfs
%dir %{_libexecdir}/glusterfs/python
%dir %{_libexecdir}/glusterfs/python/syncdaemon
     %{_libexecdir}/glusterfs/gsyncd
     %{_libexecdir}/glusterfs/python/syncdaemon/*
     %{_libexecdir}/glusterfs/gverify.sh
     %{_libexecdir}/glusterfs/set_geo_rep_pem_keys.sh
     %{_libexecdir}/glusterfs/peer_gsec_create
     %{_libexecdir}/glusterfs/peer_mountbroker
     %{_libexecdir}/glusterfs/peer_mountbroker.py*
     %{_libexecdir}/glusterfs/gfind_missing_files
     %{_libexecdir}/glusterfs/peer_georep-sshkey.py*
%{_sbindir}/gluster-georep-sshkey

       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/geo-replication
%ghost      %attr(0644,-,-) %{_sharedstatedir}/glusterd/geo-replication/gsyncd_template.conf
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/post/S56glusterd-geo-rep-create-post.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/gsync-create/pre

%dir %{_datadir}/glusterfs
%dir %{_datadir}/glusterfs/scripts
     %{_datadir}/glusterfs/scripts/get-gfid.sh
     %{_datadir}/glusterfs/scripts/slave-upgrade.sh
     %{_datadir}/glusterfs/scripts/gsync-upgrade.sh
     %{_datadir}/glusterfs/scripts/generate-gfid-file.sh
     %{_datadir}/glusterfs/scripts/gsync-sync-gfid
     %{_datadir}/glusterfs/scripts/schedule_georep.py*
%endif

%files libs
%{_libdir}/*.so.*
%exclude %{_libdir}/libgfapi.*
%if ( 0%{!?_without_tiering:1} )
# libgfdb is only needed server-side
%exclude %{_libdir}/libgfdb.*
%endif

%files -n python2-gluster
# introducing glusterfs module in site packages.
# so that all other gluster submodules can reside in the same namespace.
%dir %{python2_sitelib}/gluster
     %{python2_sitelib}/gluster/__init__.*
     %{python2_sitelib}/gluster/cliutils

%if ( 0%{!?_without_rdma:1} )
%files rdma
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport
     %{_libdir}/glusterfs/%{version}%{?prereltag}/rpc-transport/rdma*
%endif

%if ( ! 0%{_for_fedora_koji_builds} )
%files regression-tests
%dir %{_datadir}/glusterfs
     %{_datadir}/glusterfs/run-tests.sh
     %{_datadir}/glusterfs/tests
%exclude %{_datadir}/glusterfs/tests/vagrant
%endif

%if ( 0%{!?_without_ocf:1} )
%files resource-agents
# /usr/lib is the standard for OCF, also on x86_64
%{_prefix}/lib/ocf/resource.d/glusterfs
%endif

%files server
%doc extras/clear_xattrs.sh
# sysconf
%config(noreplace) %{_sysconfdir}/glusterfs
%exclude %{_sysconfdir}/glusterfs/eventsconfig.json
%exclude %{_sharedstatedir}/glusterd/nfs/nfs-server.vol
%exclude %{_sharedstatedir}/glusterd/nfs/run/nfs.pid
%if ( 0%{?_with_gnfs:1} )
%exclude %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/nfs/*
%endif
%config(noreplace) %{_sysconfdir}/sysconfig/glusterd
%if ( 0%{_for_fedora_koji_builds} )
%config(noreplace) %{_sysconfdir}/sysconfig/glusterfsd
%endif

# init files
%glusterd_svcfile
%if ( 0%{_for_fedora_koji_builds} )
%glusterfsd_svcfile
%endif
%if ( 0%{?_with_systemd:1} )
%glusterfssharedstorage_svcfile
%endif

# binaries
%{_sbindir}/glusterd
%{_sbindir}/glfsheal
%{_sbindir}/gf_attach
%{_sbindir}/gluster-setgfid2path
# {_sbindir}/glusterfsd is the actual binary, but glusterfs (client) is a
# symlink. The binary itself (and symlink) are part of the glusterfs-fuse
# package, because glusterfs-server depends on that anyway.

# Manpages
%{_mandir}/man8/gluster-setgfid2path.8*

# xlators
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/arbiter.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bit-rot.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/bitrot-stub.so
%if ( 0%{!?_without_tiering:1} )
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/changetimerecorder.so
     %{_libdir}/libgfdb.so.*
%endif
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/index.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/locks.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/posix*
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/snapview-server.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/marker.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/quota*
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/selinux.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/trash.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/upcall.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/features/leases.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/mgmt/glusterd.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/protocol/server.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage/bd.so
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/storage/posix.so
%dir %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance
     %{_libdir}/glusterfs/%{version}%{?prereltag}/xlator/performance/decompounder.so

# snap_scheduler
%{_sbindir}/snap_scheduler.py
%{_sbindir}/gcron.py
%{_sbindir}/conf.py

# /var/lib/glusterd, e.g. hookscripts, etc.
%ghost      %attr(0644,-,-) %config(noreplace) %{_sharedstatedir}/glusterd/glusterd.info
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/bitd
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/groups
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/virt
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/metadata-cache
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/gluster-block
            %attr(0644,-,-) %{_sharedstatedir}/glusterd/groups/nl-cache
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glusterfind
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glusterfind/.keys
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/glustershd
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/post/disabled-quota-root-xattr-heal.sh
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre/S28Quota-enable-root-xattr-heal.sh
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/add-brick/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/post/S10selinux-label-brick.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/create/pre
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/copy-file/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/post
                            %{_sharedstatedir}/glusterd/hooks/1/delete/post/S57glusterfind-delete-post
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/pre
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/delete/pre/S10selinux-del-fcontext.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/remove-brick/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/reset
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/reset/post
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/reset/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/post/S30samba-set.sh
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/post/S32gluster_enable_shared_storage.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/set/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/post
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/post/S29CTDBsetup.sh
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/post/S30samba-start.sh
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/start/pre
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/post
       %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/pre
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S30samba-stop.sh
            %attr(0755,-,-) %{_sharedstatedir}/glusterd/hooks/1/stop/pre/S29CTDB-teardown.sh
%config(noreplace) %ghost      %attr(0600,-,-) %{_sharedstatedir}/glusterd/options
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/peers
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/quotad
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/scrub
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/snaps
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/ss_brick
%ghost %dir %attr(0755,-,-) %{_sharedstatedir}/glusterd/vols

# Extra utility script
%dir %{_libexecdir}/glusterfs
%dir %{_datadir}/glusterfs/scripts
     %{_datadir}/glusterfs/scripts/stop-all-gluster-processes.sh
%if ( 0%{?_with_systemd:1} )
     %{_libexecdir}/glusterfs/mount-shared-storage.sh
%endif

# Incrementalapi
     %{_libexecdir}/glusterfs/glusterfind
%{_bindir}/glusterfind
     %{_libexecdir}/glusterfs/peer_add_secret_pub

%if ( 0%{?_with_firewalld:1} )
%{_prefix}/lib/firewalld/services/glusterfs.xml
%endif

# Events
%if ( 0%{!?_without_events:1} )
%files events
%config(noreplace) %{_sysconfdir}/glusterfs/eventsconfig.json
%dir %{_sharedstatedir}/glusterd
%dir %{_sharedstatedir}/glusterd/events
%dir %{_libexecdir}/glusterfs
     %{_libexecdir}/glusterfs/events
     %{_libexecdir}/glusterfs/peer_eventsapi.py*
%{_sbindir}/glustereventsd
%{_sbindir}/gluster-eventsapi
%{_datadir}/glusterfs/scripts/eventsdash.py*
%if ( 0%{?_with_systemd:1} )
%{_unitdir}/glustereventsd.service
%else
%{_sysconfdir}/init.d/glustereventsd
%endif
%endif

%changelog
* Sun Oct 14 2018 Niels de Vos <ndevos@redhat.com> - 3.12.15-1
- 3.12.15 GA
- manual systemctl daemon reload required after install (RHBZ#1497989)

* Thu Sep 6 2018 Niels de Vos <ndevos@redhat.com> - 3.12.14-1
- 3.12.14 GA

* Wed Aug 22 2018 Niels de Vos <ndevos@redhat.com> - 3.12.13-1
- 3.12.13 GA

* Thu Jul 12 2018 Niels de Vos <ndevos@redhat.com> - 3.12.12-1
- 3.12.12 GA

* Mon Jun 25 2018 Niels de Vos <ndevos@redhat.com> - 3.12.11-1
- 3.12.11 GA

* Thu Jun 14 2018 Niels de Vos <ndevos@redhat.com> - 3.12.10-1
- 3.12.10 GA

* Tue Apr 24 2018 Niels de Vos <ndevos@redhat.com> - 3.12.9-1
- 3.12.9 GA

* Fri Apr 13 2018 Niels de Vos <ndevos@redhat.com> - 3.12.8-1
- 3.12.8 GA

* Tue Mar 20 2018 Niels de Vos <ndevos@redhat.com> - 3.12.7-1
- 3.12.7 GA

* Tue Feb 13 2018 Kaleb S. KEITHLEY <kkeithle [at] redhat.com> - 3.12.6-1
- 3.12.6 GA

* Wed Jan 24 2018 Niels de Vos <ndevos@redhat.com> - 3.12.5-2
- rebuild for updated userspace-rcu

* Fri Jan 12 2018 Niels de Vos <ndevos@redhat.com> - 3.12.5-1
- 3.12.5 GA

* Thu Dec 14 2017 Niels de Vos <ndevos@redhat.com> - 3.12.4-1
- 3.12.4 GA

* Wed Nov 22 2017 Niels de Vos <ndevos@redhat.com> - 3.12.3-1
- 3.12.3 GA
- revert JWT signing support for eventsapi

* Tue Oct 31 2017 Niels de Vos <ndevos@redhat.com> - 3.12.2-2
* gfapi: set lkowner in glfd (bz#1501956)

* Fri Oct 13 2017 Niels de Vos <ndevos@redhat.com> - 3.12.2-1
- 3.12.2 GA

* Wed Sep 27 2017 Niels de Vos <ndevos@redhat.com> - 2.12.1-2
- cli: Bypass the confirmation question creating replica 2 volume with force (bz#1495858)

* Mon Sep 11 2017 Niels de Vos <ndevos@redhat.com> - 3.12.1-1
- 3.12.1 GA

* Wed Aug 30 2017 Niels de Vos <ndevos@redhat.com> - 3.12.0-1
- 3.12.0 Release Candidate GA
- Added new tool/binary to set the gfid2path xattr on files
- libibverbs-devel, librdmacm-devel -> rdma-core-devel

* Wed Aug 16 2017 Niels de Vos <ndevos@redhat.com> - 3.12.0-0.1rc0_1
- rebuilt for new userspace-rcu

* Thu Aug 10 2017 Niels de Vos <ndevos@redhat.com> - 3.12.0-0.rc0
- 3.12.0 Release Candidate 0
- various directories not owned by any package
- Add glusterfssharedstorage.service systemd file

* Sat Jul 22 2017 Niels de Vos <ndevos@redhat.com> - 3.11.2-1
- 3.11.2 GA

* Tue Jun 27 2017 Niels de Vos <ndevos@redhat.com> - 3.11.1-1
- 3.11.1 GA
- Install /var/lib/glusterd/groups/nl-cache by default

* Mon Jun 19 2017 Niels de Vos <ndevos@redhat.com> - 3.11.0-2
- Build the glusterfs-gnfs sub-package

* Tue May 30 2017 Niels de Vos <ndevos@redhat.com> - 3.11.0
- 3.11.0 GA
- Install /var/lib/glusterd/groups/gluster-block by default

* Tue May 30 2017 Niels de Vos <ndevos@redhat.com> - 3.11.0rc1
- 3.11.0 Release Candidate 1

* Tue May 16 2017 Niels de Vos <ndevos@redhat.com> - 3.11.0rc0
- 3.11.0 Release Candidate 0
- gnfs in an optional subpackage
- /var/run/gluster owner gluster:gluster(0775) for qemu(gfapi)
  statedumps (#1445569)
- Install SELinux hook scripts that manage contexts for bricks (#1047975)
- firewalld-filesystem -> firewalld (#1443959)
- the -regression-tests sub-package needs "bc" for some tests (#1442145)
- Drop dependency on psmisc, pkill is used instead of killall (#1197308)
- remove ganesha (#1418417)

* Mon May 15 2017 Niels de Vos <ndevos@redhat.com> - 3.10.2
- 3.10.2 GA

* Fri Mar 31 2017 Niels de Vos <ndevos@redhat.com> - 3.10.1
- 3.10.1 GA

* Fri Feb 24 2017  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.10.01
- 3.10.0 GA

* Wed Feb 22 2017 Niels de Vos <ndevos@redhat.com>
- 3.10.0 RC1
- Obsolete and Provide python-gluster for upgrading from glusterfs < 3.10
- revert switch to storhaug HA
- Install /var/lib/glusterd/groups/metadata-cache by default

* Tue Feb 7 2017  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.10.0-0.1rc0
- 3.10.0 RC0

* Tue Jan 17 2017  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.9.1-1
- 3.9.1 GA

* Mon Jan 16 2017  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.9.0-4
- firewalld nit

* Thu Jan 12 2017 Igor Gnatenko <ignatenko@redhat.com> - 3.9.0-3
- Rebuild for readline 7.x

* Fri Jan 6 2017  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.9.0-2
- firewalld fixes

* Tue Nov 15 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.9.0-1
- 3.9.0 GA
-  w/ glfs_free(), needed for nfs-ganesha-2.4.1 w/ patched FSAL_GLUSTER

* Mon Oct 31 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.9.0-0.3rc2
- glfs_free(), needed for nfs-ganesha-2.4.1 w/ patched FSAL_GLUSTER

* Thu Oct 27 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.9.0-0.2rc2
- portblock RA (1389293)

* Wed Oct 26 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.9.0-0.1rc2
- 3.9.0rc2

* Thu Oct 13 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.5-1
- 3.8.5 GA

* Wed Sep 21 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.4-2
- 3.8.4 GA, remove python-ctypes in rawhide per cstratak at redhat.com

* Sat Sep 10 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.4-1
- 3.8.4 GA

* Mon Aug 22 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.3-1
- 3.8.3 GA

* Wed Aug 10 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.2-1
- 3.8.2 GA

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8.1-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Fri Jul 8 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.1-1
- 3.8.1 GA

* Mon Jun 27 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.0-3
- 3.8.0 GA, http://review.gluster.org/#/c/14779/

* Wed Jun 22 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.0-2
- 3.8.0 GA, rebuild after userspace-rcu SONAME bump

* Tue Jun 14 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.0-1
- 3.8.0 GA

* Wed May 25 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.0-0.2rc2
- 3.8.0 RC2

* Mon May 16 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.8.0-0.1rc1
- 3.8.0 RC1

* Wed Apr 27 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.11-2
- %%postun libs on RHEL6 w/o firewalld

* Mon Apr 18 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.11-1
- GlusterFS 3.7.11 GA

* Fri Apr 1 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.10-1
- GlusterFS 3.7.10 GA

* Sat Mar 19 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.9-2
- glusterfs-ganesha requires cman, pacemaker, corosync on RHEL6

* Sat Mar 19 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.9-1
- GlusterFS 3.7.9 GA

* Fri Mar 4 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.8-4
- %%post, %%pre -p /sbin/ldconfig handling (1312374, 1315024)

* Fri Mar 4 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.8-3
- Requires /bin/dbus -> dbus
- quiet %%post server (1312897)
- syslog dependency (1310437)

* Fri Feb 26 2016 Niels de Vos <ndevos@redhat.com> - 3.7.8-2
- Just run /sbin/ldconfig without arguments, not as interpreter (#1312374)

* Mon Feb 8 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.8-1
- GlusterFS 3.7.8 GA

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Feb 1 2016  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.7-1
- GlusterFS 3.7.7 GA

* Mon Nov 9 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.6-2
- glusterfs-server Requires: glusterfs-api
- s/%%define/%%global/

* Mon Nov 9 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.6-1
- GlusterFS 3.7.6 GA

* Wed Oct 7 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.5-1
- GlusterFS 3.7.5 GA

* Tue Sep 1 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.4-2
- GlusterFS 3.7.4 cpio mkdir /var/lib/glusterd/hooks/1/delete/post error

* Mon Aug 31 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.4-1
- GlusterFS 3.7.4 GA

* Tue Jul 28 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.3-1
- GlusterFS 3.7.3 GA

* Tue Jun 23 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.2-3
- revised workaround for %%ghost issue

* Mon Jun 22 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.2-2
- workaround for %%ghost %%{_sharedstatedir}/glusterd/hooks/1/delete/post
  pending correct fix that also packages the .pyc and .pyo files.

* Fri Jun 19 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.2-1
- GlusterFS 3.7.2 GA

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 1 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.1-1
- GlusterFS 3.7.1 GA

* Wed May 20 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-2
- GlusterFS 3.7.0, move lib{gfdb,gfchangelog}.pc from -api-devel to -devel

* Fri May 15 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-1
- GlusterFS 3.7.0 GA

* Tue May 12 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-0.8beta2
- GlusterFS 3.7.0beta2

* Tue May 12 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-0.7beta2
- GlusterFS 3.7.0beta2, extra-xlators requires python-gluster

* Tue May 12 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-0.6beta2
- GlusterFS 3.7.0beta2, noarch python-gluster

* Tue May 12 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-0.5beta2
- GlusterFS 3.7.0beta2

* Fri May 8 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-0.4beta1
- GlusterFS 3.7.0beta1, BZ 1195947, 1218440

* Tue May 5 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-0.3beta1
- GlusterFS 3.7.0beta1, BZ 1218442

* Tue May 5 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-0.2beta1
- GlusterFS 3.7.0beta1, BZ 1218359

* Wed Apr 29 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.7.0-0.1beta1
- GlusterFS 3.7.0beta1

* Wed Apr 22 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.6.3-1
- GlusterFS 3.6.3 GA

* Wed Apr 15 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- preliminary for 3.7.0alpha

* Wed Apr 1 2015 Humble Chirammal <hchiramm@redhat.com> - 3.6.3beta2
- GlusterFS 3.6.3beta2 release.

* Thu Feb 12 2015 Humble Chirammal <hchiramm@redhat.com> - 3.6.3beta1
- GlusterFS 3.6.3beta1 release.

* Tue Feb 10 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- Ownership of /usr/lib/python2.7/site-packages/gluster, BZ 1190832
- N.B. gfapi.py was removed in 3.6 (to resurface another day?)

* Mon Feb 02 2015 Lalatendu Mohanty <lmohanty@redhat.com> - 3.6.2-2
- GlusterFS 3.6.2-2

* Fri Jan 30 2015 Nandaja Varma <nvarma@redhat.com> 1033
- remove checks for rpmbuild/mock from run-tests.sh (#178008)

* Wed Jan 28 2015  Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- glusterfs-fuse Requires: attr. See BZ 1184626, 1184627

* Thu Jan 22 2015 Lalatendu Mohanty <lmohanty@redhat.com> - 3.6.2-1
- GlusterFS 3.6.2 GA

* Thu Jan 15 2015 Lalatendu Mohanty <lmohanty@redhat.com> - 3.6.2beta2-1
- GlusterFS 3.6.2beta2

* Tue Jan 06 2015 Pranith Kumar Karampuri <pkarampu@redhat.com>
- Adding glfsheal binary

* Fri Dec 19 2014 Lalatendu Mohanty <lmohanty@redhat.com> - 3.6.2beta1-1
- GlusterFS 3.6.2beta1

* Fri Dec 12 2014 Niels de Vos <ndevos@redhat.com>
- do not package all /usr/share/glusterfs/* files in regression-tests (#1169005)

* Sat Nov 29 2014 Lalatendu Mohanty <lmohanty@redhat.com> - 3.6.1-4
- Fix build on el5 (upstream bug 1169004)

* Thu Nov 20 2014 Niels de Vos <ndevos@redhat.com> - 3.6.1-3
- Fix version in gluster-api.pc (upstream bug 1166232)

* Wed Nov 19 2014 Lalatendu Mohanty <lmohanty@redhat.com>
- Changes to remove regression-tests RPM from Fedora

* Fri Nov 07 2014 Lalatendu Mohanty <lmohanty@redhat.com>
- GlusterFS 3.6.1 GA

* Wed Oct 1 2014 Humble Chirammal <hchiramm@redhat.com>
- glusterfs-3.6.0beta3 release

* Thu Sep 25 2014  Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- add psmisc for -server
- add smarter logic to restart glusterd in %%post server

* Thu Sep 25 2014  Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- glusterfs-3.6.0beta2.tar.gz

* Wed Sep 24 2014 Balamurugan Arumugam <barumuga@redhat.com>
- remove /sbin/ldconfig as interpreter (#1145992)

* Mon Sep 22 2014  Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- More make fedora  master glusterfs spec compatible with upstream GlusterFS 3.6 spec

* Mon Sep 22 2014 Humble Chirammal <hchiramm@redhat.com>
- Make fedora  master glusterfs spec compatible with upstream GlusterFS 3.6 spec

* Fri Sep 5 2014 Lalatendu Mohanty <lmohanty@redhat.com>
- Changed the description as "GlusterFS a distributed filesystem"

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Aug 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- use upstream logrotate files exclusively (#1126788)

* Thu Jul 31 2014 Lalatendu Mohanty <lmohanty[at]redhat.com> - 3.5.2-1
- GlusterFS 3.5.2 GA

* Mon Jul 21 2014 Lalatendu Mohanty <lmohanty[at]redhat.com> - 3.5.2-0.1.beta1
- GlusterFS 3.5.2 beta1

* Wed Jul 9 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.1-2
- glusterd.init, BZ 1073217

* Fri Jun 27 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- killall --wait in %%post server (#1113959, #1113745)

* Wed Jun 25 2014 Vikhyat Umrao <vumrao@redhat.com>
- add nfs-utils package dependency for server package (#1113007)

* Tue Jun 24 2014 Lalatendu Mohanty <lmohanty[at]redhat.com> - 3.5.1-1
- GlusterFS 3.5.1 GA

* Wed Jun 11 2014 Humble Chirammal <hchiramm@redhat.com> - 3.5.1-0.3.beta2
- GlusterFS 3.5.1 beta2

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.1-0.2.beta1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon May 26 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.1-0.1.beta1
- GlusterFS 3.5.1 beta1

* Thu May 1 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-3
- syslog deprecated in Fedora20 BZ #1093318

* Fri Apr 25 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- sync with upstream glusterfs.spec.in BZ #1091392

* Wed Apr 23 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-2
- GlusterFS 3.5.0 GA, glusterfs-3.5.0-2, glusterfs.spec nits

* Thu Apr 17 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-1
- GlusterFS 3.5.0 GA

* Fri Apr 4 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-0.7.beta5
- GlusterFS 3.5.0 beta5

* Sat Mar 8 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-0.6.beta4
- GlusterFS 3.5.0 beta4

* Tue Feb 11 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-0.5.beta3
- GlusterFS 3.5.0 beta3

* Mon Jan 27 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-0.4.beta2
- GlusterFS 3.5.0 beta2

* Thu Jan 16 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-0.3.beta1
- GlusterFS 3.5.0 beta1

* Thu Jan 16 2014 Ville Skyttä <ville.skytta@iki.fi> - 3.5.0-0.2.beta1
- Drop unnecessary ldconfig calls, do remaining ones without shell.
- Drop INSTALL from docs.

* Wed Jan 15 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-0.1.beta1
- GlusterFS 3.5.0 beta1 , glusterfs-3.5.0-0.1beta1

* Fri Dec 6 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.5.0-0.1.qa3
- GlusterFS 3.5.0 QA3 , glusterfs-3.5.0-0.1qa3

* Wed Nov 6 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- obsolete glusterfs-ufo (#1025059)
- ownership of /usr/share/doc/glusterfs(-x.y.z) (#846737)
- clear_xattrs.sh belongs in /usr/share/doc/glusterfs(-x.y.z), not
  in /usr/share/doc/glusterfs-server(-x.y.z)
- remove defattr (per pkg review of another package)
- don't use %%{__foo} macros (per package review of another package)

* Sun Oct 27 2013 Niels de Vos <ndevos@redhat.com> - 3.4.1-3
- Correctly start+stop glusterfsd.service (#1022542)
- fix "warning: File listed twice: .../glusterd.info" while building

* Sat Oct 26 2013 Niels de Vos <ndevos@redhat.com>
- add base-port config option to /etc/glusterd/glusterd.vol (#1023653)

* Wed Oct 9 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- nit, sync with upstream spec

* Wed Oct 9 2013 Niels de Vos <ndevos@redhat.com>
- glusterfs-api-devel requires glusterfs-devel (#1016938, #1017094)

* Tue Oct 1 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.1-2
- resurrect /etc/init.d/glusterfsd, BUG 1014242

* Fri Sep 27 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.1-1
- GlusterFS 3.4.1 GA, glusterfs-3.4.1-1

* Thu Sep 26 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.1-0.2rc1
- scratch build for community

* Wed Sep 11 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.1-0.1qa1
- scratch build for community

* Fri Sep 6 2013 Niels de Vos <devos@fedoraproject.org>
- fix "warning: File listed twice: .../glusterd.info" while building

* Tue Aug 6 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-8
- glusterfs-server requires glusterfs-cli

* Mon Aug 5 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-7
- glusterfs requires glusterfs-libs

* Mon Aug 5 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-6
- glusterfs-cli RPM to simplify dependencies for vdsm

* Mon Aug 5 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-5
- there is no systemtap/dtrace support; don't even pretend

* Fri Aug 2 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-4
- sync changes from upstream glusterfs.spec.in, including addition of
  glusterfs-libs RPM to simplify dependencies for qemu-kvm

* Thu Jul 25 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- remove gsyncd from glusterfs, it's redundant with glusterfs-geo-rep
  ready for next build

* Thu Jul 25 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-3
- sync changes from upstream glusterfs.spec.in, and esp. glusterd.service
  from gluster w/o Wants=glusterfsd.service

* Thu Jul 18 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- sync changes from upstream glusterfs.spec.in, ready for next build

* Tue Jul 16 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-2
- tag /var/lib/glusterd/glusterd.info as %%config

* Tue Jul 16 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.2-2
- tag /var/lib/glusterd/glusterd.info as %%config

* Fri Jul 12 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-1
- GlusterFS 3.4.0 GA, glusterfs-3.4.0-1

* Mon Jul 8 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.9.beta4
- add Obsolete: glusterfs-swift where we use openstack-swift
- prerelease 3.4.0beta4 for oVirt/vdsm dependencies in Fedora19

* Fri Jul 5 2013 Niels de Vos <devos@fedoraproject.org>
- include xlators/mount/api.so in the glusterfs-api package

* Wed Jul 3 2013 Niels de Vos <devos@fedoraproject.org>
- correct AutoRequires filtering on recent Fedora (#972465)

* Fri Jun 28 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.8.beta4
- prerelease 3.4.0beta4 for oVirt/vdsm dependencies in Fedora19

* Thu Jun 27 2013 Niels de Vos <devos@fedoraproject.org>
- correct trimming the ChangeLog, keep the recent messages (#963027)
- remove the umount.glusterfs helper (#640620)

* Wed Jun 26 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.7.beta3
- prerelease 3.4.0beta3 for oVirt/vdsm dependencies in Fedora19
- libgfapi and xlator/mount/api dependency fix

* Tue Jun 11 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.6.beta3
- prerelease 3.4.0beta3 for oVirt/vdsm dependencies in Fedora19

* Wed May 29 2013 Niels de Vos <devos@fedoraproject.org>
- automatically load the fuse module on EL5
- there is no need to require the unused /usr/bin/fusermount
- fix building on EL5

* Mon May 27 2013 Niels de Vos <devos@fedoraproject.org>
- include glusterfs-api.pc in the -devel subpackage

* Fri May 24 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.5.beta2
- prerelease 3.4.0beta2 for oVirt/vdsm dependencies in Fedora19

* Thu May 9 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.4.beta1
- prerelease 3.4.0beta1 for oVirt/vdsm dependencies in Fedora19

* Wed May 8 2013 Niels de Vos <devos@fedoraproject.org>
- include all Sources and Patches into the src.rpm

* Tue May 7 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.1.beta1
- prerelease 3.4.0beta1 for oVirt/vdsm dependencies in Fedora19

* Mon Apr 29 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-14
- include backport of G4S/UFO multi-volume fix

* Fri Apr 19 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.3alpha3
- #else -> %%else, a twisty maze of passages, all alike

* Thu Apr 18 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.2alpha3
- prerelease 3.4.0alpha3 for oVirt/vdsm dependencies in Fedora19
- RHEL6 still needs the patches applied, even with grizzly
- resource-agents -> noarch

* Wed Apr 17 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.1alpha3
- prerelease 3.4.0alpha3 for oVirt/vdsm dependencies in Fedora19

* Wed Apr 17 2013 Niels de Vos <devos@fedoraproject.org> - 3.3.1-13
- remove unused requires for xlator .so files and private libraries (RHBZ#95212

* Mon Apr 15 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-12
- add glusterfs-3.3.1.rpc.rpcxprt.rdma.name.c.patch, BZ 920332
- add %%{prereltag} for upcoming 3.3.2 and 3.4.0 alpha and beta builds
- add librdmacm-devel for rdma builds

* Mon Apr 15 2013 Niels de Vos <devos@fedoraproject.org>
- Remove useless provides for xlator .so files and private libraries

* Wed Apr 10 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.4.0-0.1alpha2
- prerelease 3.4.0alpha2 for oVirt/vdsm dependencies in Fedora19

* Wed Mar 6 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-11
- /var/run/gluster - sync with gluster.org git
- Requires: portmap for rhel5 instead of rpcbind

* Tue Feb 5 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-10
- sync with glusterfs.spec(.in) from gluster.org git source

* Wed Jan 30 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-9
- essex/folsom typo, glusterfs-ufo %%files conflicts with glusterfs-swift-*

* Thu Jan 10 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-8
- revised patch to DiskFile.py for stalled GET

* Wed Jan 9 2013 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-7
- additional file ownerships and associated %%ghosts from upstream
- add BuildRequires libaio-devel to auto-enable AIO in configure,
  overlooked since 3.3.1-1.

* Fri Dec 21 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-6
- fix object get, missing iter_hook param in DiskFile::__init__

* Mon Dec 17 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-5
- Update to OpenStack Swift 1.7.4 (Folsom)

* Fri Dec 7 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-4
- Swift+UFO, now with less swift forkage. Specifically the only patches
  to swift are those already used for the Fedora openstack-swift packages
  _plus_ our backport of the upstream constraints config changes that have
  been accepted into grizzly.

* Fri Nov 16 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-3
- add Requires: rpcbind for minimum install systems where rpcbind isn't
  installed; usually this is a no-op.
- Better logic to preserve contents of /etc/glusterd

* Wed Oct 31 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-2
- Synchronize with openstack-swift-1.4.8 packaging changes, including
  systemd .service files and align with the matching sets of patches

* Thu Oct 11 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.1-1
- GlusterFS-3.3.1
- save swift .conf files correctly during upgrade
- fix glusterd restart in %%post geo-replication

* Wed Sep 19 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-11
- condrestart glusterfsd then glusterd in %%preun server

* Wed Sep 19 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-10
- fix additional python dependencies, esp. for rhel

* Tue Sep 18 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-9
- python-paste-deploy on RHEL 6, glusterfsd.init

* Thu Sep 13 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-8
- fix for glusterfs SEGV, BZ 856704, revised

* Wed Sep 12 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-7
- fix for glusterfs SEGV, BZ 856704

* Fri Sep 7 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-6
- glusterfs.spec cleanup

* Mon Aug 27 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.7-2
- fix SEGV in glusterd-rpc-ops.c, BZ 837684, f17 only.

* Sun Aug 12 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-5
- now with UFO (openstack-swift) except on el5

* Fri Aug 10 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-4
- now with UFO (openstack-swift)

* Wed Jul 18 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-3
- fix segv in cmd_heal_volume_brick_out (RHEL seems particularly
  sensitive to this bug.)

* Thu Jul 5 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-2
- selected fixes to glusterfs.spec for BZs 826836, 826855, 829734, 834847

* Thu May 31 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.3.0-1
- Update to 3.3.0

* Wed May 9 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.6-2
- Add BuildRequires: libxml2-devel, BZ 819916

* Wed Mar 21 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.6-1
- Update to 3.2.6

* Thu Feb 16 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.5-8
- rename patch files

* Mon Jan 16 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.5-7
- patch configure.ac to compile -O2 instead of -O0 on Linux.

* Tue Jan 10 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.5-6
- glusterd.init use /run per Fedora File System Layout, or /var/run when
  needed

* Tue Jan 3 2012 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.5-5
- revised spec for init.d for fedora<=16, rhel<=6; native systemd for
  f17 and rhel7

* Wed Dec 7 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.5-4
- revised sysconfig and init.d scripts. (glusterfsd.{init,sysconfig,service}
  should go away, as glusterd is responsible for starting and stopping it.)

* Wed Nov 23 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.5-3
- revised libglusterfs/src/Makefile.* to (re)enable parallel make

* Mon Nov 21 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.5-2
- rhel/epel, init.d for <=6, native systemd for 7

* Thu Nov 17 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.5-1
- Update to 3.2.5

* Wed Nov 16 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.4-3
- revised init.d/systemd to minimize fedora < 17
- get closer to the official glusterfs spec, including...
- add geo-replication, which should have been there since 3.2

* Wed Nov 2 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.4-2
- Convert init.d to systemd for f17 and later

* Fri Sep 30 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.4-1
- Update to 3.2.4

* Mon Aug 22 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.3-1
- Update to 3.2.3

* Mon Aug 22 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.2-1
- Update to 3.2.2

* Fri Aug 19 2011 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 3.2.2-0
- Update to 3.2.2

* Wed Jun 29 2011 Dan Horák <dan[at]danny.cz> - 3.2.1-3
- disable InfiniBand on s390(x) unconditionally

* Thu Jun 16 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.2.1-2
- Fix Source0 URL

* Thu Jun 16 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.2.1-1
- Update to 3.2.1

* Wed Jun 01 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.2.0-1
- Update to 3.2.0

* Tue May 10 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.4-1
- Update to 3.1.4

* Sat Mar 19 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.3-1
- Update to 3.1.3
- Merge in more upstream SPEC changes
- Remove patches from GlusterFS bugzilla #2309 and #2311
- Remove inode-gen.patch

* Sun Feb 06 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.2-3
- Add back in legacy SPEC elements to support older branches

* Thu Feb 03 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.2-2
- Add patches from CloudFS project

* Tue Jan 25 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.2-1
- Update to 3.1.2

* Wed Jan 5 2011 Dan Horák <dan[at]danny.cz> - 3.1.1-3
- no InfiniBand on s390(x)

* Sat Jan 1 2011 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.1.1-2
- Update to support readline
- Update to not parallel build

* Mon Dec 27 2010 Silas Sewell <silas@sewell.ch> - 3.1.1-1
- Update to 3.1.1
- Change package names to mirror upstream

* Mon Dec 20 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.0.7-1
- Update to 3.0.7

* Wed Jul 28 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 3.0.5-1
- Update to 3.0.x

* Sat Apr 10 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.9-2
- Move python version requires into a proper BuildRequires otherwise
  the spec always turned off python bindings as python is not part
  of buildsys-build and the chroot will never have python unless we
  require it
- Temporarily set -D_FORTIFY_SOURCE=1 until upstream fixes code
  GlusterFS Bugzilla #197 (#555728)
- Move glusterfs-volgen to devel subpackage (#555724)
- Update description (#554947)

* Sat Jan 2 2010 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.9-1
- Update to 2.0.9

* Sun Nov 8 2009 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.8-1
- Update to 2.0.8
- Remove install of glusterfs-volgen, it's properly added to
  automake upstream now

* Sat Oct 31 2009 Jonathan Steffan <jsteffan@fedoraproject.org> - 2.0.7-1
- Update to 2.0.7
- Install glusterfs-volgen, until it's properly added to automake
  by upstream
- Add macro to be able to ship more docs

* Thu Sep 17 2009 Peter Lemenkov <lemenkov@gmail.com> 2.0.6-2
- Rebuilt with new fuse

* Sat Sep 12 2009 Matthias Saou <http://freshrpms.net/> 2.0.6-1
- Update to 2.0.6.
- No longer default to disable the client on RHEL5 (#522192).
- Update spec file URLs.

* Mon Jul 27 2009 Matthias Saou <http://freshrpms.net/> 2.0.4-1
- Update to 2.0.4.

* Thu Jun 11 2009 Matthias Saou <http://freshrpms.net/> 2.0.1-2
- Remove libglusterfs/src/y.tab.c to fix koji F11/devel builds.

* Sat May 16 2009 Matthias Saou <http://freshrpms.net/> 2.0.1-1
- Update to 2.0.1.

* Thu May  7 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-1
- Update to 2.0.0 final.

* Wed Apr 29 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.3.rc8
- Move glusterfsd to common, since the client has a symlink to it.

* Fri Apr 24 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.2.rc8
- Update to 2.0.0rc8.

* Sun Apr 12 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.2.rc7
- Update glusterfsd init script to the new style init.
- Update files to match the new default vol file names.
- Include logrotate for glusterfsd, use a pid file by default.
- Include logrotate for glusterfs, using killall for lack of anything better.

* Sat Apr 11 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.1.rc7
- Update to 2.0.0rc7.
- Rename "libs" to "common" and move the binary, man page and log dir there.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Matthias Saou <http://freshrpms.net/> 2.0.0-0.1.rc1
- Update to 2.0.0rc1.
- Include new libglusterfsclient.h.

* Mon Feb 16 2009 Matthias Saou <http://freshrpms.net/> 1.3.12-1
- Update to 1.3.12.
- Remove no longer needed ocreat patch.

* Thu Jul 17 2008 Matthias Saou <http://freshrpms.net/> 1.3.10-1
- Update to 1.3.10.
- Remove mount patch, it's been included upstream now.

* Fri May 16 2008 Matthias Saou <http://freshrpms.net/> 1.3.9-1
- Update to 1.3.9.

* Fri May  9 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-1
- Update to 1.3.8 final.

* Wed Apr 23 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.10
- Include short patch to include fixes from latest TLA 751.

* Tue Apr 22 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.9
- Update to 1.3.8pre6.
- Include glusterfs binary in both the client and server packages, now that
  glusterfsd is a symlink to it instead of a separate binary.

* Sun Feb  3 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.8
- Add python version check and disable bindings for version < 2.4.

* Sun Feb  3 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.7
- Add --without client rpmbuild option, make it the default for RHEL (no fuse).
  (I hope "rhel" is the proper default macro name, couldn't find it...)

* Wed Jan 30 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.6
- Add --without ibverbs rpmbuild option to the package.

* Mon Jan 14 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.5
- Update to current TLA again, patch-636 which fixes the known segfaults.

* Thu Jan 10 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.4
- Downgrade to glusterfs--mainline--2.5--patch-628 which is more stable.

* Tue Jan  8 2008 Matthias Saou <http://freshrpms.net/> 1.3.8-0.3
- Update to current TLA snapshot.
- Include umount.glusterfs wrapper script (really needed? dunno).
- Include patch to mount wrapper to avoid multiple identical mounts.

* Sun Dec 30 2007 Matthias Saou <http://freshrpms.net/> 1.3.8-0.1
- Update to current TLA snapshot, which includes "volume-name=" fstab option.

* Mon Dec  3 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-6
- Re-add the /var/log/glusterfs directory in the client sub-package (required).
- Include custom patch to support vol= in fstab for -n glusterfs client option.

* Mon Nov 26 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-4
- Re-enable libibverbs.
- Check and update License field to GPLv3+.
- Add glusterfs-common obsoletes, to provide upgrade path from old packages.
- Include patch to add mode to O_CREATE opens.

* Thu Nov 22 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-3
- Remove Makefile* files from examples.
- Include RHEL/Fedora type init script, since the included ones don't do.

* Wed Nov 21 2007 Matthias Saou <http://freshrpms.net/> 1.3.7-1
- Major spec file cleanup.
- Add missing %%clean section.
- Fix ldconfig calls (weren't set for the proper sub-package).

* Sat Aug 4 2007 Matt Paine <matt@mattsoftware.com> - 1.3.pre7
- Added support to build rpm without ibverbs support (use --without ibverbs
  switch)

* Sun Jul 15 2007 Matt Paine <matt@mattsoftware.com> - 1.3.pre6
- Initial spec file
