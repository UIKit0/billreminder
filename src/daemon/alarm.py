#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Alarm', 'NotifyMessage']

from lib import common
from lib import utils
from lib import i18n

import dbus_manager

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

        self.__interface = dbus_manager.get_interface('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
        self.__interface.connect_to_signal('ActionInvoked', self.__on_action_invoked)

        self.parent = parent

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
        if arg[0] != self.__id:
            return

        self.parent.dbus_server.show_main_window()

        print self.__action_func
        if self.__action_func:
            self.__action_func(arg)

    def _set_id(self, id):
        self.__id = id

    def _notify_error(self, e):
        print str(e)

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
