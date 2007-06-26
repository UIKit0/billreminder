#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Daemon', 'Program', 'lock', 'unlock']

__error = False

import os
import sys

try:
    import gobject
except ImportError:
    print 'Required package: python-gobject'
    __error = True
try:
    import dbus
except ImportError:
    print 'Required package: dbus-python'
    __error = True
try:
    import pysqlite2
except ImportError:
    print 'Required package: python-pysqlite2'
    __error = True

if __error:
    raise SystemExit

from lib import common
from lib import config
from lib import i18n
from lib.actions import Actions

import alarm
import dbus_manager
from device import *

stdout_orig = sys.stdout
stderr_orig = sys.stderr

LOCKFD = None

def lock():
    """ Verify/Create Lock File """
    global LOCKFD

    try:
        LOCKFD = os.open(common.DAEMON_LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        os.write(LOCKFD, '%d' % os.getpid())
        return True
    except OSError:
        # Already locked
        return False

def unlock():
    """ Remove Lock File """
    global LOCKFD

    if not LOCKFD:
        return False
    try:
        os.close(LOCKFD)
        os.remove(common.DAEMON_LOCK_FILE)
        return True
    except OSError:
        return False


class Daemon(object):
    """ Make the program run like a daemon """
    def __init__(self):
        """ Detach process and run it as a daemon """
        if not '--no-daemon' in sys.argv:
            # Fork first child
            try: 
                pid = os.fork()
            except OSError, err:
                print >> sys.stderr, ('Unexpected error:', sys.exc_info()[0], err)

            if pid == 0:
                os.setsid()

                # Fork second child
                try:
                    pid = os.fork()
                except OSError, err:
                    print >> sys.stderr, ('Unexpected error:', sys.exc_info()[0], err)

                if pid == 0:
                    os.umask(0)
                else:
                    raise SystemExit
            else:
                raise SystemExit
            # Redirect STDIN, STDOUT and STDERR
            sys.stdin.close()
        if '--verbose' in sys.argv:
            sys.stdout.write('\n')
            sys.stdout = VerboseDevice(type_='stdout')
            sys.stderr = VerboseDevice(type_='stderr')
        else:
            sys.stdout = LogDevice(type_='stdout')
            sys.stderr = LogDevice(type_='stderr')


class Program(Daemon):
    """ BillReminder Daemon Main class """

    def __init__(self):

        # Verify if Lock File exist
        if not lock(): 
            print _('Lock File found: Maybe you have another' \
                    ' instance running.')

        # Verify if there is another Billreminder-Daemon DBus Service
        if dbus_manager.verify_service(common.DBUS_INTERFACE):
            print _('BillReminder is already running.')
            raise SystemExit

        Daemon.__init__(self)

        self.client_pid = None

        self.config = config.Config()
        self.actions = Actions()
        self.dbus_server = dbus_manager.Server(self)
        self.alarm = alarm.Alarm(self)

        # Create the mainloop
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def __del__(self):
        try:
            unlock()
        except:
            pass

    def quit(self):
        """ Close program """
        self.mainloop.quit()
        unlock()

def main():
    gobject.threads_init()

    try:
        Program()
    except KeyboardInterrupt:
        unlock()
        print >> stdout_orig, 'Keyboard Interrupt (Ctrl+C)'
    except:
        unlock()
        raise SystemExit
