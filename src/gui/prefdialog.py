#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import time
import datetime
import locale
import gobject
import lib.common as common
import lib.utils as utils
from lib import i18n

class PrefDialog(gtk.Dialog):
    """
    Class used to generate dialog to allow user to edit preferences.
    """
    def __init__(self, parent=None):
    	title = _("Preferences")
        gtk.Dialog.__init__(self, title=title, parent=parent, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, buttons=(gtk.STOCK_HELP, gtk.RESPONSE_REJECT, gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))
        self.set_icon_from_file(common.APP_ICON)
