#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class AboutDialog(gtk.Dialog):
    """
    About dialog class.
    """
    def __init__(self, parent=None):
        title = "About BillReminder"

        gtk.Dialog.__init__(self, title=title, parent=parent, flags=gtk.DIALOG_MODAL, buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

        if parent:
            self.set_transient_for(parent)
            self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        # Set up the UI
        self._initialize_dialog_widgets()

    def _initialize_dialog_widgets(self):
        self.notebook = gtk.Notebook()

        self.vbox.pack_start(self.notebook, expand=False, fill=True, padding=10)

        # Show all widgets
        self.show_all()
