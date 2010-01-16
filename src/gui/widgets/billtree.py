# - coding: utf-8 -

# Copyright (C) 2006-2010  Og Maciel <ogmaciel@gnome.org>

# This file is part of BillReminder.

# Project Hamster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Project Hamster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Project Hamster.  If not, see <http://www.gnu.org/licenses/>.


# The core code of this class is an adaptation of the code developed for the Hamster Project.
# Copyright (C) 2008-2009 Toms Bauģis <toms.baugis at gmail.com>.

import gtk
import gobject
import locale
from lib import i18n
from lib import utils

(CAT_ICON, CAT_NAME, PAYEE, DUEDATE, AMOUNT, BILL) = range(6)

class BillTree(gtk.TreeView):
    __gsignals__ = {
        "bill_clicked": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
        "double-click": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
    }

    def __init__(self):
        gtk.TreeView.__init__(self)

        self.set_headers_visible(True)
        self.set_rules_hint(True)

        self.store_model = gtk.TreeStore(gtk.gdk.Pixbuf, str, str, str, str, gobject.TYPE_PYOBJECT)
        self.set_model(self.store_model)

        # Category Icon
        cat_icon_cell = gtk.CellRendererPixbuf()
        cat_icon_cell.set_property('xalign', 0.5)
        cat_icon_column = gtk.TreeViewColumn("", cat_icon_cell, pixbuf=CAT_ICON)
        cat_icon_column.set_resizable(False)
        cat_icon_column.set_clickable(True)
        cat_icon_column.set_expand(False)
        self.append_column(cat_icon_column)

        # Category Name
        cat_name_cell = gtk.CellRendererText()
        cat_name_column = gtk.TreeViewColumn(_("Category"), cat_name_cell, text=CAT_NAME)
        cat_name_column.set_resizable(True)
        cat_name_column.set_clickable(True)
        cat_name_column.set_sort_column_id(CAT_NAME)
        self.append_column(cat_name_column)

        # Payee Name
        payee_cell = gtk.CellRendererText()
        payee_column = gtk.TreeViewColumn(_("Payee"), payee_cell, text=PAYEE)
        payee_column.set_cell_data_func(payee_cell, self.payee_cell_data_function)
        self.append_column(payee_column)

        # Due Date
        due_date_cell = gtk.CellRendererText()
        due_date_column = gtk.TreeViewColumn(_("Date"), due_date_cell, text=DUEDATE,)
        due_date_column.set_cell_data_func(due_date_cell, self.duedate_cell_data_function)
        self.append_column(due_date_column)

        # Amount Due
        amount_cell = gtk.CellRendererText()
        amount_label = "%s (%s)" % (_('Amount'), locale.localeconv()['currency_symbol'])
        amount_column = gtk.TreeViewColumn(amount_label, amount_cell, text=AMOUNT)
        amount_column.set_cell_data_func(amount_cell, self.amountdue_cell_data_function)
        self.append_column(amount_column)

        # Connect events
        self.connect("row-activated", self._on_row_activated)
        self.connect("cursor-changed", self._on_cursor_changed)
        self.connect("button-press-event", self._on_button_pressed)

        # Set the search function to search by payee when pressing keys
        self.set_search_column(PAYEE)
        self.set_search_equal_func(self._search_payee)
        self.set_enable_search(True)

        self.show()

    def payee_cell_data_function(self, column, cell, model, iter):
        column.set_resizable(True)
        column.set_clickable(True)
        column.set_expand(True)
        column.set_sort_column_id(PAYEE)

    def duedate_cell_data_function(self, column, cell, model, iter):
        bill = model.get_value(iter, BILL)
        dueDate = bill.dueDate.strftime(_('%m/%d').encode('ASCII'))
        cell.set_property('text', dueDate)
        cell.set_property('xalign', 0.5)
        column.set_resizable(False)
        column.set_clickable(True)
        column.set_sort_column_id(DUEDATE)

    def amountdue_cell_data_function(self, column, cell, model, iter):
        bill = model.get_value(iter, BILL)
        amount = utils.float_to_currency(bill.amount)
        cell.set_property('text', amount)
        cell.set_property('xalign', 1.0)
        column.set_resizable(True)
        column.set_clickable(True)
        column.set_sort_column_id(AMOUNT)

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
        if iter:
            return model[iter][5]
        else:
            return None

    def _search_payee(self, model, column, key, iter):
        bill = model.get_value(iter, BILL)
        payee = bill.payee
        # Compare the value typed (key) with payee text
        if key.lower() in payee.lower():
            return False
        return True

    def _on_cursor_changed(self, tree):
        self.emit("bill_clicked", self.get_selected_bill())
        return True

    def _on_row_activated(self, tree, path, column):
        print "_on_row_activated"
        if path:
            print "jackpot!"
            self.emit_stop_by_name ('row-activated')
            self.emit("bill_clicked", self.get_selected_bill())
            return True

    def _on_button_pressed(self, tree, event):
        if event.button == 3 and event.type == gtk.gdk.BUTTON_PRESS:
            print self.get_selected_bill()
            self.emit("bill_clicked", self.get_selected_bill())
            return True
        return False
