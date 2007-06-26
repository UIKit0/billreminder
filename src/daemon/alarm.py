#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Alarm', 'NotifyMessage']

from sys import stderr
import datetime
import time
from gobject import timeout_add
from subprocess import Popen

from lib import common
from lib import i18n
from lib.utils import Message, verify_pid

from dbus_manager import get_interface

class NotifyMessage(object):

    def __init__(self, parent):
        """ Constructor """
        self.title = common.APPNAME
        self.__replaces_id = 0
        self.icon = common.APP_HEADER
        self.summary = ''
        self.body = ''
        self.__actions = []
        self.hints = {}
        self.expire_timeout = 1000
        self.__action_func = None
        self.parent = parent

        # Connect DBus notification interface
        self.__interface = get_interface(common.NOTIFICATION_INTERFACE, common.NOTIFICATION_PATH)
        self.__interface.connect_to_signal('ActionInvoked', self.__on_action_invoked)


    def add_action(self, action):
        self.__actions.append(action)

    def set_timeout(self, expire_timeout):
        self.expire_timeout = expire_timeout * 1000

    def get_hints(self, tray):
        hints = {}
        if tray:
           x = tray.get_geometry()[1].x
           y = tray.get_geometry()[1].y
           w = tray.get_geometry()[1].width
           h = tray.get_geometry()[1].height
           x += w/2
           if y < 100:
              # top-panel
              y += h/2
           else:
              # bottom-panel
              y -= h/2
           hints['x'] = x
           hints['y'] = y
        hints['desktop-entry'] = 'billreminder'
        self.hints = hints
        return hints

    def set_action(self, func):
        self.__action_func = func

    def __on_action_invoked(self, *arg):
        # Ignore notifications from another programs
        if not arg[0] == self.__id:
            return

        # Send DBus 'show_main_window' signal
        self.parent.dbus_server.show_main_window()

        # Verify if there is a specific function to call
        if self.__action_func:
            self.__action_func(arg)
        # If client is not running, launch it
        elif not self.parent.client_pid or not verify_pid(self.parent.client_pid):
                 gui = Popen('python billreminder', shell=True)
                 self.parent.client_pid = gui.pid

    def _set_id(self, id):
        self.__id = id

    def _notify_error(self, e):
        print >> stderr, str(e)

    def Notify(self):
        if self.__interface:
            self.__interface.Notify(self.title,
                self.__replaces_id,
                self.icon,
                self.summary,
                self.body,
                self.__actions,
                self.hints,
                self.expire_timeout,
                reply_handler=self._set_id,
                error_handler=self._notify_error)

class Alarm(object):

    def __init__(self, parent):
        self.parent = parent
        self.tray_hints = {}
        self.interval = self.parent.config.getint('Alarm', 'interval') * 1000
        self.time = self.parent.config.getfloat('Alarm', 'show_alarm_at_time')
        if self.parent.config.getboolean('Alarm', 'show_startup_notification'):
            self.show_pay_notification()
        if self.interval:
            timeout_add(self.interval, self.timer)

    def show(self, title, body, show=True):
        if self.parent.config.getboolean('Alarm', 'use_alert_dialog'):
            self.show_alert(title, body, show)
        else:
            self.show_notification(title, body, show)

    def show_alert(self, title, body, show=True):
        self.parent.dbus_server.show_alert(title, body, 'info')
        if show:
            message = Message()
            message.ShowInfo(text=body, title=title)

    def show_notification(self, title, body, show=True):
        self.parent.dbus_server.show_notification(title, body, 10, common.APP_HEADER)
        if show:
            notify = NotifyMessage(self.parent)
            notify.title = title
            notify.body = body
            notify.set_timeout(10)
            notify.hints = self.tray_hints
            notify.Notify()

    def show_pay_notification(self, show=True):
        today = time.mktime(datetime.date.today().timetuple())
        limit = self.parent.config.getint('Alarm', 'notification_days_limit') * 86400.0
        if limit:
            records = self.parent.actions.get_bills('dueDate <= %s AND paid = 0' % (today + limit))
        else:
            records = self.parent.actions.get_bills('paid = 0')

        msg = N_('You have %s outstanding bill to pay!',
                 'You have %s outstanding bills to pay!', len(records)) % len(records)

        if msg:
            self.show_notification(common.APPNAME, msg, show)

        return msg

    def timer(self):
        # TODO: Show custom alarms
        print self.time
        return True
