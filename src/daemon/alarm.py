#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Alarm']

from sys import stderr
import datetime
import time
from gobject import timeout_add
from subprocess import Popen

from lib import common
from lib import i18n
from lib.bubble import NotifyMessage
from lib.utils import verify_pid, Message
from lib import dialogs
from lib.bill import Bill


class Alarm(object):

    def __init__(self, parent):
        self.parent = parent
        self.tray_hints = {}
        self.interval = self.parent.config.getint('Alarm', 'interval') * 1000
        self.time = self.parent.config.getfloat('Alarm', 'show_alarm_at_time')
        self.parent = parent
        self.tray_hints = {}
        start_delay = self.parent.config.getint('General', 'delay') * 1000
        print start_delay
        timeout_add(start_delay, self.start)

    def start(self):
        if self.parent.config.getboolean('Alarm', 'show_startup_notification'):
            self.show_pay_notification()
        self.verify_matured()
        if self.interval:
            timeout_add(self.interval, self.timer)

    def notification(self, title, body):
        notify = NotifyMessage(self.parent)
        notify.title = title
        notify.body = body
        notify.set_timeout(10)
        notify.set_default_action(self.__cb_launch_gui)
        notify.hints = self.tray_hints
        return notify

    def show_pay_notification(self):
        today = time.mktime(datetime.date.today().timetuple())
        limit = self.parent.config.getint('Alarm', 'notification_days_limit') * 86400.0
        if limit:
            records = self.parent.actions.get_bills('dueDate <= %s AND paid = 0' % (today + limit))
        else:
            records = self.parent.actions.get_bills('paid = 0')

        msg = N_('You have %s outstanding bill to pay!',
                 'You have %s outstanding bills to pay!', len(records)) % len(records)
        if msg and records:
            bubble = self.notification(common.APPNAME, msg)
            bubble.add_action("view", _("Show BillReminder"), self.__cb_launch_gui, None)
            bubble.add_action("close", _("Cancel"), None)
            bubble.show()

        return msg

    def verify_matured(self):
        today = time.mktime(datetime.date.today().timetuple())
        records = self.parent.actions.get_bills('dueDate < %s AND paid = 0' % today)

        i = 1
        for bill in records:
            timeout_add(i * 12000, self.show_bill_notification, bill)
            i += 1

    def show_bill_notification(self, bill=None):

        msg = _('The bill %s is due.') % "<b>\"%s\"</b>" % bill['payee']
        if msg:
            bubble = self.notification(common.APPNAME, msg)
            bubble.add_action("paid", _("Mark as paid"), self.__cb_mark_as_paid, bill)
            bubble.add_action("edit", _("Edit"), self.__cb_edit_bill, bill)
            bubble.add_action("close", _("Cancel"), None)
            bubble.show()


    def __cb_launch_gui(self, *arg):
    # If client is not running, launch it
        # Send DBus 'show_main_window' signal
        self.parent.dbus_server.show_main_window()
        if not self.parent.client_pid or not verify_pid(self.parent.client_pid):
            gui = Popen('python billreminder', shell=True)
            self.parent.client_pid = gui.pid

    def __cb_mark_as_paid(self, *arg):
        record = arg[1][0]
        if record:
            record['paid'] = 1
            try:
                # Edit bill to database
                self.parent.dbus_server.edit_bill(record)
            except Exception, e:
                print str(e)

    def __cb_edit_bill(self, *arg):
        record = dialogs.edit_dialog(Bill(arg[1][0]))
        if record:
            try:
                # Edit bill to database
                self.parent.dbus_server.edit_bill(record.Dictionary)
            except Exception, e:
                print str(e)

    def timer(self):
        # TODO: Show custom alarms
        print self.time
        return True
