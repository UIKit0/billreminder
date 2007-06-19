#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

try:
    import gtk
except ImportError:
    print "Please install gtk"
    raise SystemExit

try:
    import pygtk
    pygtk.require("2.0")
except ImportError:
    print "Please install pygtk"
    raise SystemExit

try:
    from gui.aboutdialog import AboutDialog
    from gui.adddialog import AddDialog
except ImportError, e:
    print str(e)
    raise SystemExit

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

def edit_dialog(record, parent=None):
    dialog = AddDialog(title="Edit a record", parent=parent, record=record)
    response = dialog.run()
    # Checks if the user did not cancel the action
    if response == -3: #gtk.RESPONSE_OK:
        record = dialog.get_record()
    dialog.destroy()

    return response, record
