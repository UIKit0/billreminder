#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import datetime
import locale
import utils
import gobject
from bill import Bill
from dal import DAL

class AddDialog(gtk.Dialog):
    """
    Class used to generate dialog to allow user to enter/edit records.
    """
    def __init__(self, title=None, parent=None, record=None):
        gtk.Dialog.__init__(self, title=title, parent=parent, flags=gtk.DIALOG_MODAL, buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
         )

        if parent:
            self.set_transient_for(parent)
            self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        # Private copy of any record passed
        self.currentrecord = record

        # Set up the UI
        self._initialize_dialog_widgets()

        # If a record was passed, we're in edit mode
        if record:
            self._populate_fields()

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
        self.calendar.mark_day(datetime.datetime.today().day)
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
        ### Populate combobox with payee from database
        self._populate_payee()
        self.amount = gtk.Entry()
        self.notesdock = gtk.ScrolledWindow()
        self.notesdock .set_shadow_type(gtk.SHADOW_OUT)
        self.notesdock .set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.notes = gtk.TextView()
        self.notesdock.add_with_viewport(self.notes)
        ### Buffer object for Notes field
        self.txtbuffer = self.notes.get_buffer()
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

    def _populate_fields(self):
        self.decimal_sep = locale.localeconv()['mon_decimal_point']
        self.thousands_sep = locale.localeconv()['mon_thousands_sep']
        
        self.allowed_digts = [self.decimal_sep , self.thousands_sep]
        # Format the amount field
        self.amount.set_text("%0.2f" % self.currentrecord.AmountDue)
        # Format the dueDate field
        dt = datetime.datetime.fromtimestamp(self.currentrecord.DueDate)
        self.calendar.select_day(dt.day)
        self.calendar.select_month(dt.month - 1, dt.year)
        utils.select_combo_text(self.payee, self.currentrecord.Payee)
        self.txtbuffer.set_text(self.currentrecord.Notes)
        #self.chkPaid.set_active(self.currentrecord.Paid)

    def _populate_payee(self):
        """ Populates combobox with existing payees """
        # Connects to the database
        dal = DAL()

        # List of payees from database
        payees = []
        records = dal.get('tblbills', "paid IN (0,1) ORDER BY payee ASC")
        for rec in records:
            if rec['payee'] not in payees:
                payees.append(rec['payee'])

        store = gtk.ListStore(gobject.TYPE_STRING)
        for payee in payees:
            store.append([payee])

        self.payee.set_model(store)
        self.payee.set_text_column(0)
        self.payeeEntry = self.payee.child
        self.selectedText = ''

    def _get_payee(self):
        """ Extracts information typed into comboboxentry """
        if self.payee.get_active_iter() is not None:
            model = self.payee.get_model()
            iteration = self.payee.get_active_iter()
            if iteration:
                return model.get_value(iteration, 0)
        else:
            return self.payeeEntry.get_text()

    def _get_record(self):
        # Extracts the date off the calendar widget
        day = self.calendar.get_date()[2]
        month = self.calendar.get_date()[1] + 1
        year = self.calendar.get_date()[0]
        # Create datetime object
        selectedDate = datetime.datetime(year, month, day)
        # Turn it into a time object
        selectedDate = time.mktime(selectedDate.timetuple())

        #buffer = self.txtNotes.get_buffer()
        startiter, enditer = self.txtbuffer.get_bounds()
        sbuffer = self.txtbuffer.get_text(startiter, enditer)

        # Gets the payee
        payee = self._get_payee()

        # Validate form
        if len(payee.strip()) == 0 or len(self.amount.get_text().strip()) == 0:
            return None, None

        if self.currentrecord is None:
            # Create a new object
            self.currentrecord = Bill(payee, selectedDate, self.amount.get_text(), sbuffer)
            #self.currentrecord = Bill(payee, selectedDate, self.amount.get_text(), sbuffer, int(self.chkPaid.get_active()))
        else:
            # Edit existing bill
            self.currentrecord.Payee = payee
            self.currentrecord.DueDate = int(selectedDate)
            self.currentrecord.AmountDue = float(self.amount.get_text())
            self.currentrecord.Notes = sbuffer
            #self.currentrecord.Paid = int(self.chkPaid.get_active())

        #return the bill
        return self.bill