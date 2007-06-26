#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from lib import i18n

# Application info
APPNAME = _("BillReminder")
APPVERSION = "0.3"
COPYRIGHTS = _("BillReminder - Copyright (c) 2006, 2007\nOg Maciel <omaciel@foresightlinux.org>")
WEBSITE = "http://billreminder.sourceforge.net"
AUTHORS = [
    _('Developers:'),
    'Og Maciel <OgMaciel@ubuntu.com>',
    'Laudeci Oliveira <laudeci@gmail.com>',
    'Luiz Armesto <luiz.armesto@gmail.com>',
    '',
    _('Contributors:'),
    'Giovanni Deganni <tiefox@gmail.com>',
    'Ruivaldo <ruivaldo@gmail.com>',
    'Mario Danic <pygi@gmail.com>'
]

ARTISTS = [
    'Led Style <ledstyle@gmail.com>',
    'Vinicius Depizzol <vdepizzol@gmail.com>'
]

LICENSE = """
This application is distributed under the BSD 
Licensing scheme.  An online version of the 
license can be obtained from 
http://www.opensource.org/licenses/bsd-license.html.

Copyright (c) 2006, 2007, Og Maciel
All rights reserved.
"""

# Media path
if os.path.exists(os.path.abspath('../images/')):
    IMAGE_PATH = os.path.abspath('../images/')
else:
    IMAGE_PATH = '/usr/share/billreminder/images'

# Images
APP_ICON = os.path.join(IMAGE_PATH, 'billreminder.png')
APP_HEADER = os.path.join(IMAGE_PATH, 'header.png')

# Config info
CFG_NAME = 'billreminder.cfg'
CFG_PATH =  os.path.expanduser('~/.config/billreminder/')

# Database info
DB_NAME = 'billreminder.db'
DB_PATH =  os.path.expanduser('~/.config/billreminder/data/')

# DBus info
DBUS_INTERFACE = 'org.gnome.Billreminder.Daemon'
DBUS_PATH = '/org/gnome/Billreminder/Daemon'

# Notification info
NOTIFICATION_INTERFACE = 'org.freedesktop.Notifications'
NOTIFICATION_PATH = '/org/freedesktop/Notifications'

# Daemon files
DAEMON_LOCK_FILE = '/tmp/billreminderd.pid'
DAEMON_LOG_FILE = '/tmp/billreminderd.log'
