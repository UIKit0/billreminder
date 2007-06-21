#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Server', 'get_interface', 'verify_service']

import dbus
import dbus.service

from lib import common
from lib.utils import force_string

from lib import bill

# Set up DBus event loop
try:
    # dbus-python 0.80 and later
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
except ImportError:
    # dbus-python prior to 0.80
    import dbus.glib


def get_interface(interface, path):
    try:
        session_bus = dbus.SessionBus()
        obj = session_bus.get_object(interface, path)
        ret = dbus.Interface(obj, interface)
        return ret
    except dbus.DBusException:
        return None

def verify_service(my_interface):
    """ Verify if a specific DBus service is running """
    try:
        interface = get_interface('org.freedesktop.DBus', '/org/freedesktop/DBus')
        return my_interface in interface.ListNames()
    except dbus.DBusException:
        return False


class Server(dbus.service.Object):
    """ DBus Service """
        
    def __init__(self, parent):
        self.parent = parent
        self.dal = self.parent.dal
        self.actions = self.parent.actions
        
        # Start DBus support
        self.__session_bus = dbus.SessionBus()
        self.__bus_name = dbus.service.BusName(common.DBUS_INTERFACE, bus=self.__session_bus)
                
        dbus.service.Object.__init__(self, self.__bus_name, common.DBUS_PATH)
    

    # DBus Methods (Called via DBus Service)
    @dbus.service.method(common.DBUS_INTERFACE, out_signature='s')
    def hello(self):
        return 'Runnig %s Daemon %s' % (common.APPNAME, common.APPVERSION)
        
    @dbus.service.method(common.DBUS_INTERFACE, out_signature='b')
    def quit(self):
        self.parent.quit()
        return True
    
    @dbus.service.method(common.DBUS_INTERFACE, in_signature='a{ss}', out_signature='aa{ss}')
    def get_bills(self, kwargs):
        """ Returns one or more records that meet the criteria passed """
        print kwargs
        ret = []
        records = self.actions.get_bills(kwargs)
        for record in records:
            ret.append(force_string(record))
        print ret
        return ret
        
    @dbus.service.method(common.DBUS_INTERFACE, in_signature='s', out_signature='aa{ss}')
    def get_bills_(self, kwargs):
        """ Returns one or more records that meet the criteria passed """
        print kwargs
        ret = []
        records = self.actions.get_bills(kwargs)
        for record in records:
            ret.append(force_string(record))
        print ret
        return ret
    
    @dbus.service.method(common.DBUS_INTERFACE, in_signature='a{ss}', out_signature='a{ss}')
    def edit_bill(self, kwargs):
        """ Edit a record in the database """
        ret = self.actions.edit_bill(kwargs)
        if ret:
            self.bill_edited(ret)
        return force_string(ret)
        
    @dbus.service.method(common.DBUS_INTERFACE, in_signature='a{ss}', out_signature='a{ss}')
    def add_bill(self, kwargs):
        """ Edit a record in the database """
        ret = self.actions.add_bill(kwargs)
        if ret:
            self.bill_added(kwargs)
        return force_string(ret)

    @dbus.service.method(common.DBUS_INTERFACE, in_signature='i', out_signature='b')
    def delete_bill(self, key):
        """ Delete a record in the database """
        ret = self.actions.delete_bill(key)
        if ret:
            self.bill_deleted(key)
        return ret
        
    @dbus.service.method(common.DBUS_INTERFACE, in_signature='a{ss}')
    def set_tray_hints(self, hints):
        # Set tray icon hints
        hints['x'] = int(hints['x'])
        hints['y'] = int(hints['y'])
        self.parent.tray_hints = hints
    
    @dbus.service.method(common.DBUS_INTERFACE, out_signature='s')
    def get_notification_message(self):
        return self.parent.show_pay_notification(show=False)
        
    @dbus.service.method(common.DBUS_INTERFACE, in_signature='ss', out_signature='b')
    def show_message(self, title, msg):
        self.parent.show_notification(title, msg)
        return True
    
    
    # DBus Signals      
    @dbus.service.signal(common.DBUS_INTERFACE, signature='a{ss}')
    def bill_added(self, kwargs):
        print 'Signal Emmited: bill_added'
          
    @dbus.service.signal(common.DBUS_INTERFACE, signature='a{ss}')
    def bill_edited(self, kwargs):
        print 'Signal Emmited: bill_edited'
    
    @dbus.service.signal(common.DBUS_INTERFACE, signature='i')
    def bill_deleted(self, key):
        print 'Signal Emmited: bill_deleted'

    @dbus.service.signal(common.DBUS_INTERFACE, signature='ssis')
    def show_notification(self, title, body, timeout, icon):
        print 'Signal Emmited: show_notification'
    
    @dbus.service.signal(common.DBUS_INTERFACE, signature='sss')
    def show_alert(self, title, body, type_):
        print 'Signal Emmited: show_alert'

    @dbus.service.signal(common.DBUS_INTERFACE)
    def show_main_window(self):
        print 'Signal Emmited: show_main_window'
