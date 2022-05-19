## statprof.py
## Copyright (C) 2012 Bryan O'Sullivan <bos@serpentine.com>
## Copyright (C) 2011 Alex Fraser <alex at phatcore dot com>
## Copyright (C) 2004,2005 Andy Wingo <wingo at pobox dot com>
## Copyright (C) 2001 Rob Browning <rlb at defaultvalue dot org>

## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 2.1 of the License, or (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with this program; if not, contact:
##
## Free Software Foundation           Voice:  +1-617-542-5942
## 59 Temple Place - Suite 330        Fax:    +1-617-542-2652
## Boston, MA  02111-1307,  USA       gnu@gnu.org

"""
statprof is intended to be a fairly simple statistical profiler for
python. It was ported directly from a statistical profiler for guile,
also named statprof, available from guile-lib [0].

[0] http://wingolog.org/software/guile-lib/statprof/

To start profiling, call statprof.start():
>>> start()

Then run whatever it is that you want to profile, for example:
>>> import test.pystone; test.pystone.pystones()

Then stop the profiling and print out the results:
>>> stop()
>>> display()
  %   cumulative      self
 time    seconds   seconds  name
 26.72      1.40      0.37  pystone.py:79:Proc0
 13.79      0.56      0.19  pystone.py:133:Proc1
 13.79      0.19      0.19  pystone.py:208:Proc8
 10.34      0.16      0.14  pystone.py:229:Func2
  6.90      0.10      0.10  pystone.py:45:__init__
  4.31      0.16      0.06  pystone.py:53:copy
    ...

All of the numerical data is statistically approximate. In the
following column descriptions, and in all of statprof, "time" refers
to execution time (both user and system), not wall clock time.

% time
    The percent of the time spent inside the procedure itself (not
    counting children).

cumulative seconds
    The total number of seconds spent in the procedure, including
    children.

self seconds
    The total number of seconds spent in the procedure itself (not
    counting children).

name
    The name of the procedure.

By default statprof keeps the data collected from previous runs. If you
want to clear the collected data, call reset():
>>> reset()

reset() can also be used to change the sampling frequency from the
default of 1000 Hz. For example, to tell statprof to sample 50 times a
second:
>>> reset(50)

This means that statprof will sample the call stack after every 1/50 of
a second of user + system time spent running on behalf of the python
process. When your process is idle (for example, blocking in a read(),
as is the case at the listener), the clock does not advance. For this
reason statprof is not currently not suitable for profiling io-bound
operations.

The profiler uses the hash of the code object itself to identify the
procedures, so it won't confuse different procedures with the same name.
They will show up as two different rows in the output.

Right now the profiler is quite simplistic.  I cannot provide
call-graphs or other higher level information.  What you see in the
table is pretty much all there is. Patches are welcome :-)


Threading
---------

Because signals only get delivered to the main thread in Python,
statprof only profiles the main thread. However because the time
reporting function uses per-process timers, the results can be
significantly off if other threads' work patterns are not similar to the
main thread's work patterns.
"""


from __future__ import division

import os
import signal


__all__ = ['start', 'stop', 'reset', 'display']


###########################################################################
## Utils

def clock():
    times = os.times()
    return times[0] + times[1]


###########################################################################
## Collection data structures

class ProfileState(object):
    def __init__(self, frequency=None):
        self.reset(frequency)

    def reset(self, frequency=None):
        # total so far
        self.accumulated_time = 0.0
        # start_time when timer is active
        self.last_start_time = None
        # total count of sampler calls
        self.sample_count = 0
        # a float
        if frequency:
            self.sample_interval = 1.0/frequency
        elif not hasattr(self, 'sample_interval'):
            # default to 1000 Hz
            self.sample_interval = 1.0/1000.0
        else:
            # leave the frequency as it was
            pass
        self.remaining_prof_time = None
        # for user start/stop nesting
        self.profile_level = 0
        # whether to catch apply-frame
        self.count_calls = False
        # gc time between start() and stop()
        self.gc_time_taken = 0

    def accumulate_time(self, stop_time):
        self.accumulated_time += stop_time - self.last_start_time

state = ProfileState()

class CodeKey(object):
    cache = {}

    __slots__ = ('filename', 'lineno', 'name')

    def __init__(self, frame):
        code = frame.f_code
        self.filename = code.co_filename
        self.lineno = frame.f_lineno
        self.name = code.co_name

    def __eq__(self, other):
        try:
            return (self.lineno == other.lineno and
                    self.filename == other.filename)
        except:
            return False

    def __hash__(self):
        return hash((self.lineno, self.filename))

    @classmethod
    def get(cls, frame):
        k = (frame.f_code.co_filename, frame.f_lineno)
        try:
            return cls.cache[k]
        except KeyError:
            v = cls(frame)
            cls.cache[k] = v
            return v

class CallData(object):
    all_calls = {}

    __slots__ = ('key', 'call_count', 'cum_sample_count', 'self_sample_count')

    def __init__(self, key):
        self.key = key
        self.call_count = 0
        self.cum_sample_count = 0
        self.self_sample_count = 0

    @classmethod
    def get(cls, key):
        try:
            return cls.all_calls[key]
        except KeyError:
            v = CallData(key)
            cls.all_calls[key] = v
            return v


###########################################################################
## SIGPROF handler

def sample_stack_procs(frame):
    state.sample_count += 1
    key = CodeKey.get(frame)
    CallData.get(key).self_sample_count += 1

    keys_seen = set()
    while frame:
        key = CodeKey.get(frame)
        keys_seen.add(key)
        frame = frame.f_back
    for key in keys_seen:
        CallData.get(key).cum_sample_count += 1

def profile_signal_handler(signum, frame):
    if state.profile_level > 0:
        state.accumulate_time(clock())
        sample_stack_procs(frame)
        signal.setitimer(signal.ITIMER_PROF,
            state.sample_interval, 0.0)
        state.last_start_time = clock()


###########################################################################
## Profiling API

def is_active():
    return state.profile_level > 0

def start():
    '''Install the profiling signal handler, and start profiling.'''
    state.profile_level += 1
    if state.profile_level == 1:
        state.last_start_time = clock()
        rpt = state.remaining_prof_time
        state.remaining_prof_time = None
        signal.signal(signal.SIGPROF, profile_signal_handler)
        signal.setitimer(signal.ITIMER_PROF,
            rpt or state.sample_interval, 0.0)
        state.gc_time_taken = 0 # dunno

def stop():
    '''Stop profiling, and uninstall the profiling signal handler.'''
    state.profile_level -= 1
    if state.profile_level == 0:
        state.accumulate_time(clock())
        state.last_start_time = None
        rpt = signal.setitimer(signal.ITIMER_PROF, 0.0, 0.0)
        signal.signal(signal.SIGPROF, signal.SIG_IGN)
        state.remaining_prof_time = rpt[0]
        state.gc_time_taken = 0 # dunno

def reset(frequency=None):
    '''Clear out the state of the profiler.  Do not call while the
    profiler is running.

    The optional frequency argument specifies the number of samples to
    collect per second.'''
    assert state.profile_level == 0, "Can't reset() while statprof is running"
    CallData.all_calls.clear()
    CodeKey.cache.clear()
    state.reset(frequency)


###########################################################################
## Reporting API

class CallStats(object):
    def __init__(self, call_data):
        self_samples = call_data.self_sample_count
        cum_samples = call_data.cum_sample_count
        nsamples = state.sample_count
        secs_per_sample = state.accumulated_time / nsamples
        basename = os.path.basename(call_data.key.filename)

        self.name = '%s:%d:%s' % (basename, call_data.key.lineno,
                                  call_data.key.name)
        self.pcnt_time_in_proc = self_samples / nsamples * 100
        self.cum_secs_in_proc = cum_samples * secs_per_sample
        self.self_secs_in_proc = self_samples * secs_per_sample
        self.num_calls = None
        self.self_secs_per_call = None
        self.cum_secs_per_call = None

    def display(self, fp):
        print(fp, ('%6.2f %9.2f %9.2f  %s' % (self.pcnt_time_in_proc,
                                                 self.cum_secs_in_proc,
                                                 self.self_secs_in_proc,
                                                 self.name)))


def display(fp=None):
    '''Print statistics, either to stdout or the given file object.'''

    if fp is None:
        import sys
        fp = sys.stdout
    if state.sample_count == 0:
        print >> fp, ('No samples recorded.')
        return

    l = [CallStats(x) for x in CallData.all_calls.values()]
    l.sort(reverse=True, key=lambda x: x.self_secs_in_proc)
    l = [(x.self_secs_in_proc, x.cum_secs_in_proc, x) for x in l]
    l = [x[2] for x in l]

    print(fp, ('%5.5s %10.10s   %7.7s  %-8.8s' %
                  ('%  ', 'cumulative', 'self', '')))
    print(fp, ('%5.5s  %9.9s  %8.8s  %-8.8s' %
                  ("time", "seconds", "seconds", "name")))

    for x in l:
        x.display(fp)

    print(fp, ('---'))
    print(fp, ('Sample count: %d' % state.sample_count))
    print(fp, ('Total time: %f seconds' % state.accumulated_time))

