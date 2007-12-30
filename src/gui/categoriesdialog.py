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

    def _initialize_dialog_widgets(self):
        self.vbox.set_spacing(8)
        self.topcontainer = gtk.HBox(homogeneous=False, spacing=0)
