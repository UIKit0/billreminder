#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class AddDialog(gtk.Dialog):
    """
    Class used to generate dialog to allow user to enter/edit records.
    """
    def __init__(self, title=None, parent=None):
        gtk.Dialog.__init__(self, title=title, parent=parent, flags=gtk.DIALOG_MODAL, buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
         )

        # Set up the UI
        self._initialize_dialog_widgets()

    def _initialize_dialog_widgets(self):
        self.vbox.set_spacing(8)
        self.topcontainer = gtk.HBox(homogeneous=False, spacing=0)
        self.calbox = gtk.VBox(homogeneous=False, spacing=0)
        self.fieldbox = gtk.VBox(homogeneous=False, spacing=0)

        # Add calendar and label
        self.callabel = gtk.Label()
        self.callabel.set_markup("<b>Due Date:</b>")
        self.callabel.set_alignment(0.00, 0.50)
        self.calendar = gtk.Calendar()
        ## Pack it all up
        self.calbox.pack_start(self.callabel, expand=True, fill=True, padding=5)
        self.calbox.pack_start(self.calendar, expand=True, fill=True, padding=5)

        # Fields
        ## Table of 3 x 2
        self.table = gtk.Table(rows=3, columns=2, homogeneous=False)
        ### Spacing to make things look better
        self.table.set_col_spacing(0, 10)
        self.table.set_row_spacing(0, 13)
        self.table.set_row_spacing(1, 13)
        self.table.set_row_spacing(2, 13)

        ## Labels
        self.payeelabel = gtk.Label()
        self.payeelabel.set_markup("<b>Payee:</b>")
        self.payeelabel.set_alignment(0.00, 0.50)
        self.amountlabel = gtk.Label()
        self.amountlabel.set_markup("<b>Amount:</b>")
        self.amountlabel.set_alignment(0.00, 0.50)
        self.noteslabel = gtk.Label()
        self.noteslabel.set_markup("<b>Note:</b>")
        self.noteslabel.set_alignment(0.00, 0.50)
        ## Fields
        self.payee = gtk.ComboBoxEntry()
        self.amount = gtk.Entry()
        self.notesdock = gtk.ScrolledWindow()
        self.notesdock .set_shadow_type(gtk.SHADOW_OUT)
        self.notesdock .set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.notes = gtk.TextView()
        self.notesdock.add_with_viewport(self.notes)
        ## Pack it all into the table
        self.table.attach(self.payeelabel, 0, 1, 0, 1, gtk.FILL, gtk.FILL)
        self.table.attach(self.amountlabel, 0, 1, 1, 2, gtk.FILL, gtk.FILL)
        self.table.attach(self.noteslabel, 0, 1, 2, 3, gtk.FILL, gtk.FILL)
        self.table.attach(self.payee, 1, 2, 0, 1, gtk.FILL, gtk.FILL)
        self.table.attach(self.amount, 1, 2, 1, 2, gtk.FILL, gtk.FILL)
        self.table.attach(self.notesdock, 1, 2, 2, 3, gtk.FILL, gtk.FILL)
        ## Pack table
        self.fieldbox.pack_start(self.table, expand=True, fill=True, padding=0)

        # Everything
        self.topcontainer.pack_start(self.calbox, expand=False, fill=False, padding=5)
        self.topcontainer.pack_start(self.fieldbox, expand=False, fill=False, padding=5)
        self.vbox.pack_start(self.topcontainer, expand=False, fill=True, padding=10)

        # Show all widgets
        self.show_all()
