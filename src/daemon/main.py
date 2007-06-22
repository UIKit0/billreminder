#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Daemon', 'Program', 'lock', 'unlock']

__error = False

import datetime
import time
import os
import sys

from lib.actions import Actions

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
from lib import dal
from lib import i18n

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
            # TODO: Create a log system
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

        self.tray_hints = {}

        self.dal = dal.DAL()
        self.actions = Actions(self.dal)
        self.dbus_server = dbus_manager.Server(self)

        self.show_pay_notification()

        # Create the mainloop
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def __del__(self):
        try:
            unlock()
        except:
            pass

    def show_notification(self, title, body, show=True):
        self.dbus_server.show_notification(title, body, 10, common.APP_HEADER)
        if show:
            notify = alarm.NotifyMessage(self)
            notify.title = title
            notify.body = body
            notify.set_timeout(10)
            notify.hints = self.tray_hints
            notify.Notify()

    def show_pay_notification(self, show=True):
        today = time.mktime(datetime.date.today().timetuple())
        limit = today + (7 * 86400.0) # TODO use config data
        records = self.actions.get_bills('dueDate <= %s AND paid = 0' % today)

        msg = N_('You have %s outstanding bill to pay!',
                 'You have %s outstanding bills to pay!', len(records)) % len(records)

        if show and msg:
            self.show_notification(_('BillReminder'), msg)

        return msg

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
