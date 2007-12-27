#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['ViewBill']

import gtk
import datetime

from gui.widgets.genericlistview import GenericListView
from lib.bill import Bill
from lib import i18n

class ViewBill(GenericListView):
    """
    This class represents a ListView for bills.
    """
    # TODO: list search

    def id_cell_data_function(self, column, cell, model, iter):
        id = model.get_value(iter, 0)
        cell.set_property('text', id)
        column.set_visible(False)

    def category_cell_data_function(self, column, cell, model, iter):
        category = model.get_value(iter, 1)
        cell.set_property('text', category)
        column.set_visible(True)

    def payee_cell_data_function(self, column, cell, model, iter):
        payee = model.get_value(iter, 2)
        paid = int(model.get_value(iter, 6))
        if not paid:
            text = '<b>%(payee)s</b>'
        else:
            text = '%(payee)s'
        cell.set_property('markup', text % {'payee': payee})

    def duedate_cell_data_function(self, column, cell, model, iter):
        dueDate = float(model.get_value (iter, 3))
        # Format the dueDate field
        dueDate = datetime.datetime.fromtimestamp(dueDate)
        # TRANSLATORS: This is a date format. You can change the order.
        dueDate = dueDate.strftime(_('%Y/%m/%d').encode('ASCII'))
        cell.set_property('text', dueDate)
        cell.set_property('xalign', 0.5)

    def amountdue_cell_data_function(self, column, cell, model, iter):
        amountDue = model.get_value(iter, 4)
        paid = int(model.get_value(iter, 6))
        amountDue = len(amountDue) > 0 and amountDue or 0
        amountDue = "%0.2f" % float(amountDue)
        if paid:
            amountDue = "<s>%s</s>" % amountDue
        cell.set_property('markup', amountDue)
        cell.set_property('xalign', 1.0)

    def notes_cell_data_function(self, column, cell, model, iter):
        notes = model.get_value (iter, 5)
        cell.set_property('text', notes)
        column.set_visible(False)

    def paid_cell_data_function(self, column, cell, model, iter):
        paid = model.get_value (iter, 6)
        cell.set_property('text', paid)
        column.set_visible(False)

    # This dictionary represents the columns displayed by the listview.
    # It is indexed by the order you want them to be displayed, followed
    # by the column title and cellrenderer type.
    columns = {
        0: ['Id',
            gtk.CellRendererText(), id_cell_data_function],
        1: [_('Category'),
            gtk.CellRendererText(), category_cell_data_function],
        2: [_('Payee'),
            gtk.CellRendererText(), payee_cell_data_function],
        3: [_('Due Date'),
            gtk.CellRendererText(), duedate_cell_data_function],
        4: [_('Amount Due'),
            gtk.CellRendererText(), amountdue_cell_data_function],
        5: [_('Notes'),
            gtk.CellRendererText(), notes_cell_data_function],
        6: [_('Paid'),
            gtk.CellRendererText(), paid_cell_data_function]
    }

    def __init__(self):
        GenericListView.__init__(self, self.columns)
        # Set the following columns to invisible
        id = self.get_column(0)
        id.set_cell_data_func(id.get_cell_renderers()[0],
                              self.id_cell_data_function)
        id.set_visible(False)

        category = self.get_column(1)
        category.set_cell_data_func(category.get_cell_renderers()[0],
                                    self.category_cell_data_function)

        payee = self.get_column(2)
        payee.set_cell_data_func(payee.get_cell_renderers()[0],
                                 self.payee_cell_data_function)

        duedate = self.get_column(3)
        duedate.set_cell_data_func(duedate.get_cell_renderers()[0],
                                   self.duedate_cell_data_function)

        amountdue = self.get_column(4)
        amountdue.set_cell_data_func(amountdue.get_cell_renderers()[0],
                                     self.amountdue_cell_data_function)

        notes = self.get_column(5)
        notes.set_cell_data_func(notes.get_cell_renderers()[0],
                                 self.notes_cell_data_function)
        notes.set_visible(False)

        paid = self.get_column(6)
        paid.set_cell_data_func(paid.get_cell_renderers()[0],
                                self.paid_cell_data_function)
        paid.set_visible(False)
