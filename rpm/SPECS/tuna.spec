%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_ver: %define python_ver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name: tuna
Version: 0.9
Release: 1%{?dist}
License: GPLv2
Summary: Application tuning GUI & command line utility
Group: Application/System
Source: http://userweb.kernel.org/~acme/tuna/%{name}-%{version}.tar.bz2
BuildArch: noarch
BuildRequires: python-devel
Requires: python-ethtool
Requires: python-linux-procfs >= 0.4.2
Requires: python-schedutils >= 0.2
# This really should be a Suggests...
# Requires: python-inet_diag
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%description
Provides interface for changing scheduler and IRQ tunables, at whole CPU and at per
thread/IRQ level. Allows isolating CPUs for use by a specific application and moving
threads and interrupts to a CPU by just dragging and dropping them. Operations can
be done on CPU sockets, understanding CPU topology.

Can be used as a command line utility without requiring the GUI libraries to be
installed.

%package -n oscilloscope
Summary: Generic Oscilloscope
Group: Application/System
Requires: python-matplotlib
Requires: python-numeric
Requires: pygtk2
Requires: tuna = %{version}-%{release}

%description -n oscilloscope
Plots stream of values read from standard input on the screen together with
statistics and a histogram.

Allows to instantly see how a signal generator, such as cyclictest, signaltest
or even ping, reacts when, for instance, its scheduling policy or real time
priority is changed, be it using tuna or plain chrt & taskset.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}
mkdir -p %{buildroot}/{%{_bindir},%{_datadir}/tuna/help/kthreads}
install -m644 tuna/tuna_gui.glade %{buildroot}/%{_datadir}/tuna/
install -m755 tuna-cmd.py %{buildroot}/%{_bindir}/tuna
install -m755 oscilloscope-cmd.py %{buildroot}/%{_bindir}/oscilloscope
install -m644 help/kthreads/* %{buildroot}/%{_datadir}/tuna/help/kthreads/

# l10n-ed message catalogues
for lng in `cat po/LINGUAS`; do
        po=po/"$lng.po"
        mkdir -p %{buildroot}/%{_datadir}/locale/${lng}/LC_MESSAGES
        msgfmt $po -o %{buildroot}/%{_datadir}/locale/${lng}/LC_MESSAGES/tuna.mo
done


%clean
rm -rf %{buildroot}

%files
%defattr(0755,root,root,0755)
%{_bindir}/tuna
%dir %{_datadir}/tuna/
%{_datadir}/tuna/tuna_gui.glade
%dir %{_datadir}/tuna/help
%dir %{_datadir}/tuna/help/kthreads/
%{_datadir}/tuna/help/kthreads/*
%{_datadir}/locale/*/LC_MESSAGES/*.mo
%{python_sitelib}/tuna/
%if "%{python_ver}" >= "2.5"
%{python_sitelib}/*.egg-info
%endif

%files -n oscilloscope
%defattr(0755,root,root,0755)
%{_bindir}/oscilloscope

%changelog
* Wed May 13 2009 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.9-1
- cmdline: add --show_sockets/-n

* Mon Oct 27 2008 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.8.4-1
- cmdline: Allow globbing --irqs/-q
- cmdline: Allow globbing --threads/-t
- cmdline: Support regex on --thread
- cmdline: Check if thread names resolved to TIDs
- irqview: We have to pass an int to schedutils.setscheduler
- irqview: Initialize the rt_prio entry box
- gui: move procview to a separate file
- gui: Move irqview to a separate file
- gui: remove the Set/set trick in tuna/tuna_gui.py, not used anymore
- gui: Use schedutils.SCHED_{OTHER,FIFO,RR}
- gui: move cpuview classes to a separate file
- gui: Stop handling exceptions at procview.set_thread_columns
- oscilloscope: Ignore invalid samples, emitting just a warning

* Mon Oct 27 2008 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.8-1
- [Non]VolCtxtSwitch columns should be represented in the GUI as unsigned
- Several spelling fixes
- Handle some more schedutils exceptions
- Fix getopt long option for --priority, it requires an arg
- Set the irq affinity mask when setting a IRQ thread affinity
- Add a --spread command line option, it will spread the threads
  passed thru --threads into the cpus specified in --cpu or --socket.

* Mon Sep 15 2008 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.7-1
- CPU topology support: operations now can be performed on CPU sockets in
  addition to individual CPUs
- --show_threads: command line now can see the same information available
  in the GUI

* Tue Aug 12 2008 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.6-1
- tuna: posix_cpu_timer is percpu but its too long to have '/' in the cmdline
- tuna: Fixup the message about what filename was really used (rtgroups)
- tuna: Save the affinity mask for non-percpu kthreads
- tuna: Ignore rtprio when changing sched policy to SCHED_OTHER

* Thu Aug  7 2008 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.5-1
- tuna_gui: Provide instructions on how to use the generated rtctl file
- tuna_gui: Add "Save kthreads tunings" menu entry in the process list box
- tuna: Implement saving current kthread sched policy and rtprio as an rtctl file
- help: Add more kernel thread help texts, written by the MRG crew

* Tue Jun 17 2008 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.4-1
- oscilloscope subpackage
- oscilloscope: Allow passing the number of samples to appear on screen
- oscilloscope: use io_add_watch instead of timeout_add
- oscilloscope: check if the latency tracer is available
- oscilloscope: Allow disabling auto-scaling
- oscilloscope: group the system info and help frames in a vbox
- oscilloscope: parse X geometry parameter
- tuna: Convert widget coords to bin_window coords
- tuna: Implement --affect_children and --priority

* Fri May 16 2008 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.3-1
- Add oscilloscope command, initially useful with signaltest and cyclictest,
  but will also be used with the latencytest utility in the qpid project and
  with any other source of signals. Requires python-matplotlib, that will
  be added to the MRG repo soon. 
- Allow toggling auto-refresh from the irq and threads views
- Changes to make tuna work on older RHEL versions, helpful when evaluating
  RHEL-RT components.
- Allow using tuna without GUI libraries installed, please see:
  tuna --help
  For available commands.
- Several fixes

* Thu Mar 27 2008 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.2-1
- Command line interface
- Remove the requirement of a GUI packages
- Allow moving one child thread to a CPU
- Status icon
- "What is this?", for now just for some kernel threads
- Add "Restore CPU" to undo "Isolate CPU"
- Faster CPU isolation process
- Allow moving IRQs & Threads to all cpus
- CPU filtering

* Mon Feb 26 2008 Arnaldo Carvalho de Melo <acme@redhat.com> - 0.1-1
- package created
