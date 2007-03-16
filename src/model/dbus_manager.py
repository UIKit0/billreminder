#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ['BillDBus', 'DaemonDBus']

import gobject
import os

import dbus
import dbus.service
try:
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
except:
    pass

import common

class BillDBus(dbus.service.Object):
    def __init__(self, window, object_path="/org/gnome/Billreminder"):
        self.window = window
        self.bus = dbus.SessionBus()
        bus_name = dbus.service.BusName("org.gnome.Billreminder", bus=self.bus)
        dbus.service.Object.__init__(self, bus_name, object_path)
        
    @dbus.service.method("org.gnome.Billreminder")
    def hello(self):
        return "Running"
        
    @dbus.service.method("org.gnome.Billreminder")
    def show_message(self, title, msg):
        self.window.notify.show_message(title, msg, 12, os.path.abspath(common.APP_HEADER))
        return "Successful command"
    
        
class DaemonDBus(dbus.service.Object):
    def __init__(self, daemon, object_path="/org/gnome/Billreminder/Daemon"):
        self.daemon = daemon
        __session_bus = dbus.SessionBus()
        __bus_name = dbus.service.BusName("org.gnome.Billreminder.Daemon", bus=__session_bus)
        dbus.service.Object.__init__(self, __bus_name, object_path)
        
    @dbus.service.method("org.gnome.Billreminder.Daemon")
    def hello(self):
        return "Running"
        
    @dbus.service.method("org.gnome.Billreminder.Daemon")
    def quit(self):
        self.daemon.mainloop.quit()
        return "Successful command"
    
    @dbus.service.method("org.gnome.Billreminder.Daemon")
    def show_notifications(self):
        self.daemon.createNotification()
        return "Successful command"