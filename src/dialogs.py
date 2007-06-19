#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

try:
    import gtk
except ImportError:
    print "Please install gtk"
    sys.exit(1)

try:
    import pygtk
    pygtk.require("2.0")
except ImportError:
    print "Please install pygtk"
    sys.exit(1)

try:
    from aboutdialog import AboutDialog
    from adddialog import AddDialog
except ImportError, e:
    print str(e)
    sys.exit(1)

def about_dialog(parent=None):
    about = AboutDialog()
    ret = about.run()
    about.destroy()

    return ret

def add_dialog(parent=None):
    record = None
    dialog = AddDialog(title="Add a new record", parent=parent)
    response = dialog.run()
    # Checks if the user did not cancel the action
    if response == -3: #gtk.RESPONSE_OK:
        record = dialog.get_record()
    dialog.destroy()

    return response, record
