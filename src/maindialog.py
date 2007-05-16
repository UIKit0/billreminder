#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

# Import widgets modules
from toolbar import Toolbar
from statusbar import Statusbar
from viewbill import ViewBill as ViewBill

# Import dialogs modules
from adddialog import AddDialog
from aboutdialog import AboutDialog

# Import data model modules
from bill import Bill
from dal import DAL

class MainDialog:

    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("BillReminder")
        self.window.set_border_width(3)
        self.window.set_size_request(500, 200)
        self.window.connect("delete_event", self.on_delete_event)

        self.box = gtk.VBox(homogeneous=False, spacing=0)

        # ViewBill
        self.list = ViewBill()
        self.list.connect('cursor_changed', self.on_list_cursor_changed)

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

        # Connects to the database
        self.dal = DAL()
        self._populateTreeView(self.dal.get('tblbills', 'paid = 0 ORDER BY dueDate DESC'))

    def _getBill(self):
        """ Returns a bill object from the current selected record """
        sel = self.list.get_selection()
        _model, iteration = sel.get_selected()

        b_id = _model.get_value(iteration, 0)

        records = self.dal.get('tblbills', {'Id': b_id})
        rec = records[0]
        
        # Return bill and id
        return b_id, Bill(rec)

    # Methods:  UI
    def _populateTreeView(self, records):
        """ Populates the treeview control with the records passed """

        # Loops through bills collection
        path = 0
        for rec in records:
            self.list.add(self._formatedRow(rec))

        self.list.set_cursor(path)
        return

    def _formatedRow(self, row):
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
        self.menubar.add_stock(gtk.STOCK_NEW, "Add a new record", self.on_mnuNew_clicked)
        self.menubar.add_stock(gtk.STOCK_EDIT, "Edit a record", self.on_mnuEdit_clicked)
        self.menubar.add_stock(gtk.STOCK_DELETE, "Delete selected record", self.on_mnuDelete_clicked)
        self.menubar.add_space()
        self.menubar.add_button(gtk.STOCK_APPLY, "Paid", "Mark as paid", self.on_mnuPaid_clicked)
        self.menubar.add_button(gtk.STOCK_UNDO, "Not Paid", "Mark as not paid", self.on_mnuNotPaid_clicked)
        self.menubar.add_space()
        self.menubar.add_stock(gtk.STOCK_ABOUT, "About the application", self.on_mnuAbout_clicked)
        self.menubar.add_space()
        self.menubar.add_stock(gtk.STOCK_CLOSE, "Quit the application", self.on_mnuQuit_clicked)

    def add_bill(self):
        dialog = AddDialog(title="Add a new record", parent=self.window)
        ret = dialog.run()
        print ret
        dialog.destroy()

    def edit_bill(self):
        dialog = AddDialog(title="Edit an existing record", parent=self.window, record=self.currentrecord)
        ret = dialog.run()
        print ret
        dialog.destroy()

    def about(self):
        about = AboutDialog(parent=self.window)
        ret = about.run()
        about.destroy()

    # Methods
    def _quit_application(self):
        gtk.main_quit()
        return False

    # Event handlers
    def on_list_cursor_changed(self, widget):
        """ 
            This function will handle the signal sent when a row is selected and 
            displays the selected record information.
        """
        # Get currently selected bill
        b_id, bill = self._getBill()

        # Keep track of current bill
        self.currentrecord = bill

        notes = bill.Notes

        # Display the status for the selected row
        self.statusbar.Notes(notes)

    def on_mnuNew_clicked(self, toolbutton):
        self.add_bill()

    def on_mnuEdit_clicked(self, toolbutton):
        self.edit_bill()

    def on_mnuDelete_clicked(self, toolbutton):
        pass

    def on_mnuPaid_clicked(self, toolbutton):
        pass

    def on_mnuNotPaid_clicked(self, toolbutton):
        pass

    def on_mnuAbout_clicked(self, toolbutton):
        self.about()

    def on_mnuQuit_clicked(self, toolbutton):
        self._quit_application()

    def on_delete_event(self, widget, event, data=None):
        self._quit_application()

def main():
    gtk.main()

if __name__ == "__main__":
    billreminder = MainDialog()
    main()