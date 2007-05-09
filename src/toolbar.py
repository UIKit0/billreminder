# spews deprecationwarnings if the 2.0 api is used. Sigh.

import gtk

class Toolbar(gtk.Toolbar):
    def __init__(self):
        gtk.Toolbar.__init__(self)

        self.set_tooltips(True)
        self.set_border_width(1)
        self._populate()

    def _populate(self):
        self.add_stock(gtk.STOCK_NEW, "Add a new record", self.on_mnuNew_clicked)
        self.add_stock(gtk.STOCK_EDIT, "Edit a record", self.on_mnuEdit_clicked)
        self.add_stock(gtk.STOCK_DELETE, "Delete selected record", self.on_mnuDelete_clicked)
        self.add_space()
        self.add_button(gtk.STOCK_APPLY, "Paid", "Mark as paid", self.on_mnuPaid_clicked)
        self.add_button(gtk.STOCK_UNDO, "Not Paid", "Mark as not paid", self.on_mnuNotPaid_clicked)
        self.add_space()
        self.add_stock(gtk.STOCK_ABOUT, "About the application", self.on_mnuAbout_clicked)
        self.add_space()
        self.add_stock(gtk.STOCK_CLOSE, "Quit the application", self.on_mnuQuit_clicked)

    def add_space(self):
        self.insert(gtk.SeparatorToolItem(), -1)

    def add_widget(self, widget, tip_text, private_text):
        toolitem = gtk.ToolItem()
        toolitem.add(widget)
        toolitem.set_expand(False)
        toolitem.set_homogeneous(False)
        toolitem.set_tooltip(gtk.Tooltips(), tip_text, private_text)
        self.insert(toolitem,-1)

    def add_button(self, image, title, tip_text=None, callback=None):
        toolitem = gtk.ToolButton(image)
        toolitem.set_label(title)
        if callback:
            toolitem.connect('clicked', callback)
        self.insert(toolitem,-1)

    def add_stock(self, stock_id, tip_text=None, callback=None):
        toolitem = gtk.ToolButton(stock_id)
        toolitem.set_tooltip(gtk.Tooltips(), tip_text, tip_text)
        if callback:
            toolitem.connect('clicked', callback)
        self.insert(toolitem,-1)

    def add_toggle(self, stock_id, title, tip_text, callback):
        toolitem = gtk.ToggleToolButton(stock_id)
        toolitem.connect('toggled', callback)
        toolitem.set_tooltip(gtk.Tooltips(), tip_text, tip_text)
        self.insert(toolitem,-1)

    # Event handling for menuitems

    def on_mnuNew_clicked(self, toolbutton):
        pass

    def on_mnuEdit_clicked(self, toolbutton):
        pass

    def on_mnuDelete_clicked(self, toolbutton):
        pass

    def on_mnuPaid_clicked(self, toolbutton):
        pass

    def on_mnuNotPaid_clicked(self, toolbutton):
        pass

    def on_mnuAbout_clicked(self, toolbutton):
        pass

    def on_mnuQuit_clicked(self, toolbutton):
        #if self.parent_controler:
        gtk.main_quit()
        return False
            #self.parent_controler.delete_event(parent, "delete_event")
