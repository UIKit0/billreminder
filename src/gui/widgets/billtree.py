# - coding: utf-8 -

import gobject
import gtk
from lib import i18n
from lib import utils

class BillTree(gtk.TreeView):
    __gsignals__ = {
        "edit-clicked": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
        "double-click": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
    }

    def __init__(self):
        gtk.TreeView.__init__(self)

        self.set_headers_visible(True)
        self.set_rules_hint(True)

        self.store_model = gtk.TreeStore(gtk.gdk.Pixbuf, str, str, str, str, gobject.TYPE_PYOBJECT)
        self.set_model(self.store_model)

        self.insert_column_with_attributes(-1, "", gtk.CellRendererPixbuf(), pixbuf=0)
        self.insert_column_with_attributes(-1, _("Category"), gtk.CellRendererText(), text=1)
        self.insert_column_with_attributes(-1, _("Payee"), gtk.CellRendererText(), text=2)
        self.insert_column_with_data_func(-1, _("Date"), gtk.CellRendererText(), self.duedate_cell_data_function)
        self.insert_column_with_data_func(-1, _("Amount"), gtk.CellRendererText(), self.amountdue_cell_data_function)
        self.insert_column_with_data_func(-1, "", gtk.CellRendererPixbuf(), self.edit_cell_data_function)

        # Set columns attributes
        for col in self.get_columns():
            col.set_resizable(True)
            col.set_clickable(True)

        self.connect("row-activated", self._on_row_activated)
        self.connect("button-release-event", self._on_button_release_event)
        self.connect("key-press-event", self._on_key_pressed)

        self.show()

    def duedate_cell_data_function(self, column, cell, model, iter):
        bill = model.get_value(iter, 5)
        dueDate = bill.dueDate.strftime(_('%m/%d').encode('ASCII'))
        cell.set_property('text', dueDate)
        cell.set_property('xalign', 1.0)
        column.set_sort_column_id(3)

    def amountdue_cell_data_function(self, column, cell, model, iter):
        bill = model.get_value(iter, 5)
        amount = bill.amount
        cell.set_property('text', amount)
        cell.set_property('xalign', 1.0)
        column.set_sort_column_id(4)

    def edit_cell_data_function(self, column, cell, model, iter):
        bill = model.get_value(iter, 5)
        cell.set_property('xalign', 1)

        if model.get_value(iter, 5) is None:
            cell.set_property("stock_id", "")
        else:
            cell.set_property("stock_id", "gtk-edit")

    def add_bill(self, bill, parent = None):

        catName = _('None')
        catColor = '#d3d7cf'

        if bill.category:
            catName = bill.category.name
            if bill.category.color:
                catColor = bill.category.color

        catIcon = utils.create_pixbuf(color=catColor)

        self.store_model.append(parent,
            [catIcon, catName, bill.payee, bill.dueDate, bill.amount, bill]
        )

    def clear(self):
        self.store_model.clear()

    def detach_model(self):
        self.set_model()

    def attach_model(self):
        self.set_model(self.store_model)
        self.expand_all()

    def get_selected_bill(self):
        selection = self.get_selection()
        (model, iter) = selection.get_selected()
        return model[iter][5]


    def _on_button_release_event(self, tree, event):
        # a hackish solution to make edit icon keyboard accessible
        pointer = event.window.get_pointer() # x, y, flags
        path = self.get_path_at_pos(pointer[0], pointer[1]) #column, innerx, innery
        column = path[1]

        if path and path[1] == self.get_column(5):
            print "jackpot!"
            self.emit("edit-clicked", self.get_selected_bill())
            return True

        return False

    def _on_row_activated(self, tree, path, column):
        print column.cell_get_position(gtk.CellRendererPixbuf())
        return False
        if column == self.edit_column:
            self.emit_stop_by_name ('row-activated')
            self.emit("edit-clicked", self.get_selected_bill())
            return True

    def _on_key_pressed(self, tree, event):
        # capture ctrl+e and pretend that user click on edit
        if (event.keyval == gtk.keysyms.e  \
              and event.state & gtk.gdk.CONTROL_MASK):
            self.emit("edit-clicked", self.get_selected_bill())
            return True

        return False
