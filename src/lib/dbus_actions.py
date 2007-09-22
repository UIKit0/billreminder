#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus
import dbus.service
import os
from subprocess import Popen

import dal
import bill
from lib import common
from lib.utils import force_string, Message
from db.billstable import BillsTable

class Actions(object):

    def __init__(self, databaselayer=None):
        try:
            session_bus = dbus.SessionBus()
            obj = session_bus.get_object(common.DBUS_INTERFACE, common.DBUS_PATH)
            self.dbus_interface = dbus.Interface(obj, common.DBUS_INTERFACE)
            pid = os.getpid()
            print self.dbus_interface.register(pid)
        except dbus.DBusException:
            if Message().ShowErrorQuestion(_("An error occurred while connecting to BillReminder Daemon!\nDo you want to launch it and restart BillReminder?")):
                Popen('python billreminderd --open-gui', shell=True)
                raise SystemExit
            return False


    def _correct_type(self, record):
        if 'Id' in record.keys():
            record['Id'] = int(record['Id'])
        if 'dueDate' in record.keys():
            record['dueDate'] = int(record['dueDate'])
        if 'amountDue' in record.keys():
            record['amountDue'] = float(record['amountDue'])
        if 'paid' in record.keys():
            record['paid'] = int(record['paid'])
        return record

    def get_bills(self, kwargs):
        """ Returns one or more records that meet the criteria passed """
        try:
            if isinstance(kwargs, basestring):
                records = self.dbus_interface.get_bills_(kwargs)
            else:
                records = self.dbus_interface.get_bills(force_string(kwargs))
            for record in records:
                record = self._correct_type(record)
            return records
        except dbus.DBusException:
            if self.__init__():
                return self.get_bills(kwargs)

    def add_bill(self, kwargs):
        """ Adds a bill to the database """
        try:
            record = self.dbus_interface.add_bill(force_string(kwargs))
            return self._correct_type(record)
        except dbus.DBusException:
            if self.__init__():
                return self.get_bills(kwargs)

    def edit_bill(self, kwargs):
        """ Edit a record in the database """
        try:
            record = self.dbus_interface.edit_bill(force_string(kwargs))
            return self._correct_type(record)
        except dbus.DBusException:
            if self.__init__():
                return self.get_bills(kwargs)

    def delete_bill(self, key):
        """ Delete a record in the database """
        try:
            return self.dbus_interface.delete_bill(key)
        except dbus.DBusException:
            if self.__init__():
                return self.get_bills(kwargs)
