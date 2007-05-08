#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

from toolbar import Toolbar
from statusbar import Statusbar
from bill import Bill
from viewbill import ViewBill as ListView
from dal import DAL

class MainWindow:

    # close the window and quit
    def on_delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("BillReminder")
        self.window.set_border_width(3)
        self.window.set_size_request(500, 200)
        self.window.connect("delete_event", self.on_delete_event)

        self.box = gtk.VBox(homogeneous=False, spacing=0)

        # ListView
        self.list = ListView()
        self.list.connect('cursor_changed', self.on_list_cursor_changed)

        # Menubar
        self.menubar = Toolbar()

        # ScrolledWindow
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_shadow_type(gtk.SHADOW_OUT)
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledwindow.add(self.list)

        # Statusbar
        self.statusbar = Statusbar()
        self.statusbar.push("<b>Records:</b>")

        # Pack it all up
        self.box.pack_start(self.menubar, expand=False, fill=True, padding=2)
        self.box.pack_start(self.scrolledwindow, expand=True, fill=True, padding=2)
        self.box.pack_start(self.statusbar, expand=False, fill=True, padding=2)

        self.window.add(self.box)

        self.window.show_all()

        # Connects to the database
        self.dal = DAL()
        self._populateTreeView(self.dal.get('tblbills', 'paid = 0 ORDER BY dueDate DESC'))

    def on_list_cursor_changed(self, widget):
        """ 
            This function will handle the signal sent when a row is selected and 
            displays the selected record information.
        """
        # Get currently selected bill
        b_id, bill = self._getBill()

        notes = bill.Notes

        # Display the status for the selected row
        self.statusbar.push('%s' % (notes.replace('\n', ' ')))

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

    def _getBill(self):
        """ Returns a bill object from the current selected record """
        sel = self.list.get_selection()
        _model, iteration = sel.get_selected()

        b_id = _model.get_value(iteration, 0)

        records = self.dal.get('tblbills', {'Id': b_id})
        rec = records[0]
        
        # Return bill and id
        return b_id, Bill(rec)

def main():
    gtk.main()

if __name__ == "__main__":
    billreminder = MainWindow()
    main()
