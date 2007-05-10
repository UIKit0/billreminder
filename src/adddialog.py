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

        # Set up the UI
        self._initialize_dialog_widgets()

    def _initialize_dialog_widgets(self):
        self.topcontainer = gtk.HBox(homogeneous=False, spacing=0)
        self.calbox = gtk.VBox(homogeneous=False, spacing=0)
        self.fieldbox = gtk.VBox(homogeneous=False, spacing=0)

        # Add calendar and label
        self.callabel = gtk.Label()
        self.callabel.set_markup("<b>Due Date:</b>")
        self.calendar = gtk.Calendar()
        ## Pack it all up
        self.calbox.pack_start(self.callabel, expand=True, fill=True, padding=0)
        self.calbox.pack_start(self.calendar, expand=True, fill=True, padding=0)

        # Fields
        self.table = gtk.Table(rows=3, columns=2, homogeneous=False)
        self.payeelabel = gtk.Label()
        ## Labels
        self.payeelabel.set_markup("<b>Payee:</b>")
        self.amountlabel = gtk.Label()
        self.amountlabel.set_markup("<b>Amount:</b>")
        self.noteslabel = gtk.Label()
        self.noteslabel.set_markup("<b>Note:</b>")
        ## Fields
        self.payee = gtk.ComboBoxEntry()
        self.amount = gtk.Entry()
        self.notesdock = gtk.ScrolledWindow()
        self.notesdock .set_shadow_type(gtk.SHADOW_OUT)
        self.notesdock .set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.notes = gtk.TextView()
        self.notesdock.add_with_viewport(self.notes)
        ## Pack it all into the table
        self.table.attach(self.payeelabel, 0, 1, 0, 1)
        self.table.attach(self.amountlabel, 0, 1, 1, 2)
        self.table.attach(self.noteslabel, 0, 1, 2, 3)
        self.table.attach(self.payee, 1, 2, 0, 1)
        self.table.attach(self.amount, 1, 2, 1, 2)
        self.table.attach(self.notesdock, 1, 2, 2, 3)
        ## Pack table
        self.fieldbox.pack_start(self.table)

        # Everything
        self.topcontainer.pack_start(self.calbox, expand=True, fill=True, padding=0)
        self.topcontainer.pack_start(self.fieldbox, expand=True, fill=True, padding=0)
        self.vbox.pack_start(self.topcontainer, expand=False, fill=False, padding=0)

        # Show all widgets
        self.show_all()
