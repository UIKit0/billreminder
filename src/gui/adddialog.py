#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['AddDialog']

import pygtk
pygtk.require('2.0')
import gtk
import time
import datetime
import locale
import gobject

from lib import utils
from lib import common
from lib.bill import Bill
from lib.actions import Actions
from lib import i18n
from gui.widgets.datebutton import DateButton
from gui.categoriesdialog import CategoriesDialog

class AddDialog(gtk.Dialog):
    """
    Class used to generate dialog to allow user to enter/edit records.
    """
    def __init__(self, title=None, parent=None, record=None):
        gtk.Dialog.__init__(self, title=title, parent=parent,
                            flags=gtk.DIALOG_MODAL,
                            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                     gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        self.set_icon_from_file(common.APP_ICON)

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
        # TODO: Add CATEGORY selector
        self.vbox.set_spacing(8)
        self.topcontainer = gtk.HBox(homogeneous=False, spacing=0)
        self.calbox = gtk.VBox(homogeneous=False, spacing=0)
        self.fieldbox = gtk.VBox(homogeneous=False, spacing=0)

        # Add calendar and label
        self.callabel = gtk.Label()
        self.callabel.set_markup("<b>%s: </b>" % _("Due Date"))
        self.callabel.set_alignment(0.00, 0.50)
        self.calendar = gtk.Calendar()
        self.calendar.mark_day(datetime.datetime.today().day)
        ## Pack it all up
        self.calbox.pack_start(self.callabel,
                               expand=True, fill=True, padding=5)
        self.calbox.pack_start(self.calendar,
                               expand=True, fill=True, padding=5)

        # Fields
        ## Table of 5 x 2
        self.table = gtk.Table(rows=5, columns=2, homogeneous=False)
        ### Spacing to make things look better
        self.table.set_col_spacing(0, 10)
        self.table.set_row_spacing(0, 6)
        self.table.set_row_spacing(1, 6)
        self.table.set_row_spacing(2, 6)
        self.table.set_row_spacing(3, 6)

        ## Labels
        self.payeelabel = gtk.Label()
        self.payeelabel.set_markup("<b>%s </b>" % _("Payee:"))
        self.payeelabel.set_alignment(0.00, 0.50)
        self.amountlabel = gtk.Label()
        self.amountlabel.set_markup("<b>%s </b>" % _("Amount:"))
        self.amountlabel.set_alignment(0.00, 0.50)
        self.categorylabel = gtk.Label()
        self.categorylabel.set_markup("<b>%s </b>" % _("Category:"))
        self.categorylabel.set_alignment(0.00, 0.50)
        self.noteslabel = gtk.Label()
        self.noteslabel.set_markup("<b>%s </b>" % _("Notes:"))
        self.noteslabel.set_alignment(0.00, 0.50)
        self.alarmlabel = gtk.Label()
        self.alarmlabel.set_markup("<b>%s </b>" % _("Alarm:"))
        self.alarmlabel.set_alignment(0.00, 0.50)
        ## Fields
        ### Payee
        self.payee = gtk.ComboBoxEntry()
        self.payeecompletion = gtk.EntryCompletion()
        self.payee.child.set_completion(self.payeecompletion)
        self._populate_payee() # Populate combobox with payee from db
        ### Amount
        self.amount = gtk.Entry()
        ### Category
        self.categorydock = gtk.HBox(homogeneous=False, spacing=0)
        self.category = gtk.combo_box_new_text()
        self.category.set_row_separator_func(self._determine_separator)
        self.category.connect("changed", self._on_categorycombo_changed)
        self.categorybutton = gtk.Button()
        self.categorybutton.connect("clicked",
                                    self._on_categoriesbutton_clicked)
        self.categorybutton.set_tooltip_text(_("Manage Categories"))
        self.categorybuttonimage = gtk.Image()
        self.categorybuttonimage.set_from_stock(gtk.STOCK_EDIT,
                                                gtk.ICON_SIZE_BUTTON)
        self.categorybutton.set_image(self.categorybuttonimage)
        self.categorydock.pack_start(self.category, expand=True,
                                     fill=True, padding=0)
        self.categorydock.pack_start(self.categorybutton, expand=False,
                                     fill=True, padding=0)
        self._populate_category() # Populate combobox with category from db
        ### Notes
        self.notesdock = gtk.ScrolledWindow()
        self.notesdock.set_shadow_type(gtk.SHADOW_OUT)
        self.notesdock.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.notes = gtk.TextView()
        self.notesdock.add_with_viewport(self.notes)
        ### Buffer object for Notes field
        self.txtbuffer = self.notes.get_buffer()
        ### Alarm
        self.alarm = DateButton(self)
        self.alarm.set_tooltip_text(_("Select Date and Time"))

        ## Pack it all into the table
        self.table.attach(self.payeelabel, 0, 1, 0, 1, gtk.FILL, gtk.FILL)
        self.table.attach(self.amountlabel, 0, 1, 1, 2, gtk.FILL, gtk.FILL)
        self.table.attach(self.categorylabel, 0, 1, 2, 3, gtk.FILL, gtk.FILL)
        self.table.attach(self.noteslabel, 0, 1, 3, 4, gtk.FILL, gtk.FILL)
        self.table.attach(self.alarmlabel, 0, 1, 4, 5, gtk.FILL, gtk.FILL)
        self.table.attach(self.payee, 1, 2, 0, 1, gtk.FILL, gtk.FILL)
        self.table.attach(self.amount, 1, 2, 1, 2, gtk.FILL, gtk.FILL)
        self.table.attach(self.categorydock, 1, 2, 2, 3, gtk.FILL, gtk.FILL)
        self.table.attach(self.notesdock, 1, 2, 3, 4, gtk.FILL, gtk.FILL)
        self.table.attach(self.alarm, 1, 2, 4, 5, gtk.FILL, gtk.FILL)
        ## Pack table
        self.fieldbox.pack_start(self.table, expand=True, fill=True, padding=0)

        # Everything
        self.topcontainer.pack_start(self.calbox,
                                     expand=False, fill=False, padding=5)
        self.topcontainer.pack_start(self.fieldbox,
                                     expand=False, fill=False, padding=5)
        self.vbox.pack_start(self.topcontainer,
                             expand=False, fill=True, padding=10)

        # Show all widgets
        self.show_all()

    def _determine_separator(self, model, iter, data=None):
        return model.get_value(iter, 0) == "---"

    def _populate_fields(self):
        self.decimal_sep = locale.localeconv()['mon_decimal_point']
        self.thousands_sep = locale.localeconv()['mon_thousands_sep']

        self.allowed_digts = [self.decimal_sep , self.thousands_sep]
        # Format the amount field
        self.amount.set_text("%(amount)0.2f" % \
                             {'amount': self.currentrecord.AmountDue})
        # Format the dueDate field
        dt = datetime.datetime.fromtimestamp(self.currentrecord.DueDate)
        self.calendar.select_day(dt.day)
        self.calendar.select_month(dt.month - 1, dt.year)
        utils.select_combo_text(self.payee, self.currentrecord.Payee)
        actions = Actions()
        records = actions.get_categories({'id': self.currentrecord.Category})
        if records:
            categoryname = records[0]['categoryname']
            utils.select_combo_text(self.category, categoryname)
        else:
            self.category.set_active(0)

        self.txtbuffer.set_text(self.currentrecord.Notes)
        #self.chkPaid.set_active(self.currentrecord.Paid)

    def _populate_payee(self):
        """ Populates combobox with existing payees """
        # Connects to the database
        actions = Actions()

        # List of payees from database
        payees = []
        records = actions.get_bills("paid IN (0,1) ORDER BY payee ASC")
        for rec in records:
            if rec['payee'] not in payees:
                payees.append(rec['payee'])

        store = gtk.ListStore(gobject.TYPE_STRING)
        for payee in payees:
            store.append([payee])

        self.payee.set_model(store)
        self.payeecompletion.set_model(store)
        self.payee.set_text_column(0)
        self.payeecompletion.set_text_column(0)
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

    def _populate_category(self):
        """ Populates combobox with existing categories """
        # Connects to the database
        actions = Actions()

        # List of categories from database
        categories = []
        records = actions.get_categories("")
        records = records or []

        for rec in records:
            if rec['categoryname'] not in categories:
                categories.append(rec['categoryname'])

        store = gtk.ListStore(gobject.TYPE_STRING)
        self.category.set_model(store)
        store.append([_("None")])
        store.append(["---"])

        for category in categories:
            store.append([category])
        store.append(["---"])
        store.append([_("New Category")])

    def _get_category(self):
        """ Extracts information typed into comboboxentry """
        actions = Actions()

        if self.category.get_active_iter() is not None:
            model = self.category.get_model()
            iteration = self.category.get_active_iter()
            if iteration:
                name = model.get_value(iteration, 0)
        else:
            name = None

        if not name or name == _("None"):
            return None

        records = actions.get_categories({'categoryname': name})
        if records:
            cat_id = records[0]['id']
        else:
            row = actions.add_category({'categoryname': name})
            if row:
                cat_id = row['id']
        return cat_id and int(cat_id) or None

    def get_record(self):
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

        # Gets the category
        category = self._get_category()

        # Validate form
        if len(payee.strip()) == 0 or len(self.amount.get_text().strip()) == 0:
            return None, None

        if self.currentrecord is None:
            # Create a new object
            self.currentrecord = Bill(payee, category, selectedDate,
                                      self.amount.get_text(), sbuffer)
            #self.currentrecord = Bill(payee, selectedDate,
            #                          self.amount.get_text(), sbuffer,
            #                          int(self.chkPaid.get_active()))
        else:
            # Edit existing bill
            self.currentrecord.Category = category
            self.currentrecord.Payee = payee
            self.currentrecord.DueDate = int(selectedDate)
            self.currentrecord.AmountDue = float(self.amount.get_text())
            self.currentrecord.Notes = sbuffer
            #self.currentrecord.Paid = int(self.chkPaid.get_active())

        #return the bill
        return self.currentrecord

    def _on_categoriesbutton_clicked(self, button, new=False):
        categories = CategoriesDialog(parent=self, new=new)
        ret = categories.run()

        if ret == gtk.RESPONSE_OK and new:
            categories._on_savebutton_clicked(None)

        index = self.category.get_active()
        name_before = self.category.get_model()[index][0]
        # Repopulate categories
        self._populate_category()
        name_after = self.category.get_model()[index][0]
        if ret == gtk.RESPONSE_OK:
            cat_index = categories.list.get_cursor()[0][0]
            if cat_index:
                index = cat_index + 2
        else:
            if name_after != name_before:
                index = 0

        if new:
            index = len(self.category.get_model()) - 3

        self.category.set_active(index)

        categories.destroy()
        return ret

    def _on_categorycombo_changed(self, combobox):
        index = self.category.get_active()
        if index == len(self.category.get_model()) - 1:
            self.category.set_active(self.category_index_before)
            self._on_categoriesbutton_clicked(combobox, True)
        self.category_index_before = index
