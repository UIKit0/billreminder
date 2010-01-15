#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from optparse import OptionParser
import datetime as dt

current_path = os.path.realpath(__file__)
basedir = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(os.path.join(basedir, "billreminder.py")):
    if os.path.exists(os.path.join(os.getcwd(), "billreminder.py")):
        basedir = os.getcwd()
sys.path.insert(0, basedir)
os.chdir(basedir)


try:
    import pygtk
    pygtk.require("2.0")
except ImportError:
    print "Please install pygtk"
    raise SystemExit

try:
    import gtk
except ImportError:
    print "Please install gtk"
    raise SystemExit

try:
    import sqlalchemy
except ImportError:
    print "Please install sqlalchemy"
    raise SystemExit

from lib import dialogs
from lib import common
from lib import i18n
from gui.maindialog import MainDialog as BillReminder

# migrate settings to gconf
# TODO - move to fixtures / consider for removal
if os.path.exists(os.path.join(common.USER_CFG_PATH, common.CFG_NAME)):
    from lib.migrate_to_gconf import migrate
    migrate(os.path.join(common.USER_CFG_PATH, common.CFG_NAME))


def main():
    #args = sys.argv
    parser = OptionParser()
    parser.set_usage(_("Usage:  billreminder [OPTIONS...]"))
    parser.add_option('-v','--version', action='store_true', dest='app_version', default=False, help=_('Displays the version number for this application.'))
    parser.add_option('--about', action='store_true', dest='app_about', default=False, help=_('About this application.'))
    parser.add_option('--add', action='store_true', dest='app_add', default=False, help=_('Adds a new bill to the database.'))
    parser.add_option('--standalone', action='store_true', dest='app_standalone', default=False, help=_('Access database directly, without daemon.'))
    parser.add_option('--new', action='store_true', dest='new_main', default=False)

    # Verify arguments
    options, args = parser.parse_args()


    if options.new_main:
        from gui.new import MainWindow
        app = MainWindow()
        gtk.main()

    elif options.app_about:
        dialogs.about_dialog()
    elif options.app_add:
        print dialogs.add_dialog()
    elif options.app_standalone:
        print _("This option is not implemented yet.")
    elif options.app_version:
        print _("This is %(appname)s - Version: %(version)s") % \
                         {'appname': common.APPNAME,
                          'version': common.APPVERSION}
    else:
        gtk.gdk.threads_init()
        app = BillReminder()
        gtk.main()

if __name__ == "__main__":
    main()
