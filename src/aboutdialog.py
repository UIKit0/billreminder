#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import common

LICENSE = """
This application is distributed under the BSD 
Licensing scheme.  An online version of the 
license can be obtained from 
http://www.opensource.org/licenses/bsd-license.html.

Copyright (c) 2006, 2007, Og Maciel
All rights reserved.
"""

TRANSLATORS = """
Reinout van Schouwen <reinouts@gnome.org> (nl),
Daniel Nylander <po@danielnylander.se> (sv),
Tommy Mikkelsen <tamikkelsen@gmail.com> (no),
Rolando Espinoza La Fuente <darkrho@gmail.com> (es),
Gilberto Miralla <xyhthyx@gmail.com> (es)
"""

AUTHORS = """
Og Maciel <og.maciel@gmail.com>,
Laudeci Oliveira <laudeci@gmail.com>,
Luiz Armesto <luiz.armesto@gmail.com>
"""

ARTISTS = """
"""

class AboutDialog(gtk.AboutDialog):
    """
    About dialog class.
    """
    def __init__(self, parent=None):
        gtk.AboutDialog.__init__(self)

        # Set up the UI
        self._initialize_dialog_widgets()

    def _initialize_dialog_widgets(self):
        self.set_name('BillReminder')
        self.set_version('0.3')
        self.set_copyright('Copyright (c) 2006, 2007, Og Maciel')
        self.set_logo(gtk.gdk.pixbuf_new_from_file(common.APP_HEADER))
        self.set_translator_credits(TRANSLATORS)
        self.set_license(LICENSE)
        self.set_website('http://billreminder.sourceforge.net')
        self.set_authors(AUTHORS)

        # Show all widgets
        self.show_all()

