#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class AddDialog(gtk.Dialog):
    """
    Class used to generate dialog to allow user to enter/edit records.
    """
    def __init__(self, title=None, parent=None):
        gtk.Dialog.__init__(self, title=title, parent=parent)

    def _initialize_dialog_widgets(self):
        pass
