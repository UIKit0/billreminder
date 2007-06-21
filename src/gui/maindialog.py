#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

# Import widgets modules
from gui.widgets.toolbar import Toolbar
from gui.widgets.statusbar import Statusbar
from gui.widgets.viewbill import ViewBill as ViewBill

# Import dialogs modules
#from gui.adddialog import AddDialog

# Import data model modules
from lib.bill import Bill
from lib.dal import DAL
from lib.actions import Actions

# Import common utilities
import lib.common as common
import lib.dialogs as dialogs

class MainDialog:

    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("%s - %s" % (common.APPNAME, common.APPVERSION))
        self.window.set_border_width(3)
        self.window.set_size_request(550, 300)
        self.window.set_icon_from_file(common.APP_ICON)
        self.window.connect("delete_event", self.on_delete_event)

        self.box = gtk.VBox(homogeneous=False, spacing=0)

        # ViewBill
        self.list = ViewBill()
        self.list.connect('cursor_changed', self._on_list_cursor_changed)

        # Menubar
        self.menubar = Toolbar()
        self._populate_menubar()

        # ScrolledWindow
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_shadow_type(gtk.SHADOW_OUT)
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledwindow.add(self.list)

        # Statusbar
        self.statusbar = Statusbar()

        # Pack it all up
        self.box.pack_start(self.menubar, expand=False, fill=True, padding=2)
        self.box.pack_start(self.scrolledwindow, expand=True, fill=True, padding=2)
        self.box.pack_start(self.statusbar, expand=False, fill=True, padding=2)

        self.window.add(self.box)

        self.window.show_all()

        self.toggle_buttons()

        # Connects to the database
        self.actions = Actions()
        self._populateTreeView(self.actions.get_bills('paid = 0 ORDER BY dueDate DESC'))

    # Methods:  UI
    def _get_selected_record(self):
        """ Returns a bill object from the current selected record """
        if len(self.list.listStore) > 0:
            selection = self.list.get_selection()
            _model, iteration = selection.get_selected()

            b_id = _model.get_value(iteration, 0)

            try:
                records = self.actions.get_bills({'Id': b_id})
                self.currentrecord = Bill(records[0])
            except Exception, e:
                print str(e)
                self.currentrecord = None
        else:
            self.currentrecord = None

    def _populateTreeView(self, records):
        """ Populates the treeview control with the records passed """

        # Loops through bills collection
        path = 0
        for rec in records:
            self.list.add(self._formated_row(rec))

        self.list.set_cursor(path)
        return

    def _formated_row(self, row):
        """ Formats a bill to be displayed as a row. """
        # Make sure the row is created using fields in proper order
        fields = ['Id', 'payee', 'dueDate', 'amountDue', 'notes', 'paid']
        # Initial list
        formated = []
        # Loop through 'fields' and color code them
        for key in fields:
                formated.append(row[key])

        return formated

    def _populate_menubar(self):
        self.btnNew = self.menubar.add_button(gtk.STOCK_NEW, "New","Add a new record", self.on_btnNew_clicked)
        self.btnEdit = self.menubar.add_button(gtk.STOCK_EDIT, "Edit", "Edit a record", self.on_btnEdit_clicked)
        self.btnRemove = self.menubar.add_button(gtk.STOCK_DELETE, "Delete", "Delete selected record", self.on_btnDelete_clicked)
        self.menubar.add_space()
        self.btnPaid = self.menubar.add_button(gtk.STOCK_APPLY, "Paid", "Mark as paid", self.on_btnPaid_clicked)
        self.btnUnpaid = self.menubar.add_button(gtk.STOCK_UNDO, "Not Paid", "Mark as not paid", self.on_btnPaid_clicked)
        self.menubar.add_space()
        self.btnAbout = self.menubar.add_button(gtk.STOCK_ABOUT, "About", "About the application", self.on_btnAbout_clicked)
        self.menubar.add_space()
        self.btnClose = self.menubar.add_button(gtk.STOCK_CLOSE, "Close", "Quit the application", self.on_btnQuit_clicked)

    def add_bill(self):
        record = dialogs.add_dialog(parent=self.window)

        # Checks if the user did not cancel the action
        if record:
            # Add new bill to database
            bill = self.actions.add_bill(record.Dictionary)
            if bill:
                self.list.add(self._formated_row(bill))
                self._update_statusbar()
                #self.bill_id = id_
                #self.refreshBillList(False)

    def edit_bill(self):
        record = dialogs.edit_dialog(parent=self.window, record=self.currentrecord)

        # Checks if the user did not cancel the action
        if record:
            try:
                # Edit bill to database
                self.actions.edit_bill(record.Dictionary)
                # Update list with updated record
                idx = self.list.get_cursor()[0][0]
                self.list.listStore[idx] = self._formated_row(record.Dictionary)
                self._update_statusbar(idx)
            except Exception, e:
                print str(e)

    def remove_bill(self):
        try:
            if self.actions.delete_bill(self.currentrecord.Id):
                self.list.remove()
                self._update_statusbar()
        except Exception, e:
            print str(e)

    def toggle_bill_paid(self):
        # Toggle paid field
        self.currentrecord.Paid = (self.currentrecord.Paid == 0) and 1 or 0

        try:
            # Edit bill to database
            self.actions.edit_bill(self.currentrecord.Dictionary)
            # Update list with updated record
            idx = self.list.get_cursor()[0][0]
            self.list.listStore[idx] = self._formated_row(self.currentrecord.Dictionary)
            self._update_statusbar(idx)
        except Exception, e:
            print str(e)

    def about(self):
        dialogs.about_dialog(parent=self.window)

    # Methods
    def _quit_application(self):
        gtk.main_quit()
        return False

    def toggle_buttons(self, paid=None):
        """ Toggles all buttons conform number of records present and their state """
        if len(self.list.listStore) > 0:
            self.btnEdit.set_sensitive(True)
            self.btnRemove.set_sensitive(True)
            """
            Enable/disable paid and unpiad buttons.
            If paid = True, paid button and menu will be enabled.
            """
            if paid:
                self.btnPaid.set_sensitive(False)
                self.btnUnpaid.set_sensitive(True)
            else:
                self.btnPaid.set_sensitive(True)
                self.btnUnpaid.set_sensitive(False)
        else:
            self.btnEdit.set_sensitive(False)
            self.btnRemove.set_sensitive(False)
            self.btnPaid.set_sensitive(False)
            self.btnUnpaid.set_sensitive(False)

    def _update_statusbar(self, index=0):
        """ This function is used to update status bar informations about the list """
        records = len(self.list.listStore)

        # Record count
        self.statusbar.Records(records)
        if self.currentrecord:
            # Display the status for the selected row
            self.statusbar.Notes(self.currentrecord.Notes)
            # Toggles toolbar buttons on/off
            self.toggle_buttons(self.currentrecord.Paid)

    # Event handlers
    def _on_list_cursor_changed(self, widget):
        # Get currently selected bill
        self._get_selected_record()
        # Update statusbar
        self._update_statusbar()

    def on_btnNew_clicked(self, toolbutton):
        self.add_bill()

    def on_btnEdit_clicked(self, toolbutton):
        self.edit_bill()

    def on_btnDelete_clicked(self, toolbutton):
        self.remove_bill()

    def on_btnPaid_clicked(self, toolbutton):
        self.toggle_bill_paid()

    def on_btnAbout_clicked(self, toolbutton):
        self.about()

    def on_btnQuit_clicked(self, toolbutton):
        self._quit_application()

    def on_delete_event(self, widget, event, data=None):
        self._quit_application()

def main():
    gtk.main()

if __name__ == "__main__":
    billreminder = MainDialog()
    main()
