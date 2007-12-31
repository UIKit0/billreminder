#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['CategoriesDialog']

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from lib.actions import Actions
from lib import common
from lib import i18n
from gui.widgets.viewcategory import ViewCategory
from db.categoriestable import CategoriesTable

class CategoriesDialog(gtk.Dialog):
    """
    Class used to generate dialog to allow user to enter/edit categories.
    """
    def __init__(self, parent=None):
        gtk.Dialog.__init__(self, title=_("Categories Manager"),
                            parent=parent, flags=gtk.DIALOG_MODAL,
                            buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.set_icon_from_file(common.APP_ICON)

        if parent:
            self.set_transient_for(parent)
            self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        # Set up the UI
        self._initialize_dialog_widgets()
        #self._populate_fields()
        self.actions = Actions()
        self._populateTreeView(self.actions.get_categories(""))

    def _initialize_dialog_widgets(self):
        self.vbox.set_spacing(8)
        self.topcontainer = gtk.Frame("<b>%s</b>" % _("Categories"))
        self.topcontainer.props.label_widget.set_use_markup(True)
        self.topcontainer.set_shadow_type(gtk.SHADOW_NONE)
        self.topcontainer_alignment = gtk.Alignment()
        self.topcontainer_alignment.set_padding(10, 0, 12, 0)
        self.topcontainer.add(self.topcontainer_alignment)
        self.fieldbox = gtk.VBox(homogeneous=False, spacing=6)

        self.list = ViewCategory()
        self.list.set_size_request(300, 150)

        # ScrolledWindow
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_shadow_type(gtk.SHADOW_OUT)
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,
                                       gtk.POLICY_AUTOMATIC)
        self.scrolledwindow.add(self.list)

        self.table = gtk.Table(rows=2, columns=2, homogeneous=False)
        self.table.set_col_spacing(0, 6)
        self.table.set_row_spacing(0, 6)

        self.namelabel = gtk.Label()
        self.namelabel.set_markup("%s " % _("Name:"))
        self.namelabel.set_alignment(0.00, 0.50)
        self.colorlabel = gtk.Label()
        self.colorlabel.set_markup("%s " % _("Color:"))
        self.colorlabel.set_alignment(0.00, 0.50)

        self.name_ = gtk.Entry()
        self.color = gtk.ColorButton()

        self.table.attach(self.namelabel, 0, 1, 0, 1, gtk.FILL, gtk.FILL)
        self.table.attach(self.colorlabel, 0, 1, 1, 2, gtk.FILL, gtk.FILL)
        self.table.attach(self.name_, 1, 2, 0, 1)
        self.table.attach(self.color, 1, 2, 1, 2)

        self.actions = gtk.HButtonBox()
        self.actions.set_layout(gtk.BUTTONBOX_END)
        self.actions.set_spacing(6)

        self.newbutton = gtk.Button(stock=gtk.STOCK_NEW)
        self.savebutton = gtk.Button(stock=gtk.STOCK_SAVE)
        self.deletebutton = gtk.Button(stock=gtk.STOCK_DELETE)

        self.actions.pack_start(self.newbutton)
        self.actions.pack_start(self.savebutton)
        self.actions.pack_start(self.deletebutton)

        self.fieldbox.pack_start(self.scrolledwindow,
                                     expand=True, fill=True)
        self.fieldbox.pack_start(self.table,
                                     expand=False, fill=True)
        self.fieldbox.pack_start(self.actions,
                                     expand=False, fill=True)
        self.topcontainer_alignment.add(self.fieldbox)
        self.vbox.pack_start(self.topcontainer,
                             expand=True, fill=True, padding=10)

        # Show all widgets
        self.show_all()


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
        fields = CategoriesTable.Fields
        # Initial list
        formated = []
        # Loop through 'fields' and color code them
        for key in fields:
            if len(formated) == 1:
                formated.append(None)
            formated.append(row[key])
        print formated
        return formated
