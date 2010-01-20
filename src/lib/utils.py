# -*- coding: utf-8 -*-

__all__ = ['ContextMenu', 'Message']

import sys
import os
import cairo
import datetime
import locale
import StringIO

try:
    import pygtk
    pygtk.require("2.0")
    import dbus
    import dbus.service
except:
      pass

try:
    import gtk
except ImportError, e:
    print str(e)
    raise SystemExit

from lib import i18n


def load_ui_file(name):
    import common
    ui = gtk.Builder()
    ui.add_from_file(os.path.join(common.DEFAULT_CFG_PATH, name))
    return ui


class ContextMenu(gtk.Menu):
    """ Creates context menus accessed by mouse right click. """
    def __init__(self, *args):
        gtk.Menu.__init__(self)
        self.menuItem = None

    def addMenuItem(self, menuName, actionFunction=None, menuImage=None,
                          forceName=False, isCheck=False):
        """ Add itens to menu.

            @menuName is the text showed in the menu option.
                    If you pass a - (minus) as parameter value,
                    it will create a separation menu item.
            @actionFunction is the procedure called when activate
                    signal is triggered from the menu.
        """
        if menuName == "-":
            menuItem = gtk.SeparatorMenuItem()
        else:
            if menuImage is not None:
                if isinstance(menuImage, gtk.Image):
                    menuItem = gtk.ImageMenuItem(menuName)
                    menuItem.set_image(menuImage)
                else:
                    if not forceName:
                        menuItem = gtk.ImageMenuItem(menuImage)
                    else:
                        menuItem = gtk.ImageMenuItem(menuName)
                        img = gtk.Image()
                        img.set_from_stock(menuImage, gtk.ICON_SIZE_MENU)
                        menuItem.set_image(img)
            elif isCheck:
                menuItem = gtk.CheckMenuItem(menuName)
            else:
                menuItem = gtk.ImageMenuItem(menuName)

            if actionFunction is not None and not isCheck:
                menuItem.connect("activate", actionFunction)
            elif actionFunction is not None and isCheck:
                menuItem.connect("toggled", actionFunction)
        menuItem.show()
        self.append(menuItem)
        self.menuItem = menuItem
        return menuItem

class Message:
    """ Generic prompt dialog """
    _title_format = '<span weight="bold" size="larger">%s</span>'

    def ShowQuestionYesNo(self, text, parentWindow=None, title=''):
        dlg = gtk.MessageDialog (parentWindow,
                                 gtk.DIALOG_MODAL,
                                 gtk.MESSAGE_QUESTION,
                                 gtk.BUTTONS_YES_NO)
        # Dialog Title
        title = title and title or _('Question')
        dlg.set_markup(self._title_format % title)
        dlg.format_secondary_markup(text)
        response = dlg.run()
        dlg.destroy()
        return response == gtk.RESPONSE_YES

    def ShowError(self, text, parentWindow=None, title=''):
        dlg = gtk.MessageDialog(parentWindow,
                               gtk.DIALOG_MODAL,
                               gtk.MESSAGE_ERROR,
                               gtk.BUTTONS_OK)
        # Dialog Title
        title = title and title or _('Error')
        dlg.set_markup(self._title_format % title)
        dlg.format_secondary_markup(text)
        dlg.run()
        dlg.destroy()
        return

    def ShowErrorQuestion(self, text, parentWindow=None, title=''):
        dlg = gtk.MessageDialog(parentWindow,
                               gtk.DIALOG_MODAL,
                               gtk.MESSAGE_ERROR,
                               gtk.BUTTONS_YES_NO)
        # Dialog Title
        title = title and title or _('Error')
        dlg.set_markup(self._title_format % title)
        dlg.format_secondary_markup(text)
        response = dlg.run()
        dlg.destroy()
        return response == gtk.RESPONSE_YES

    def ShowInfo(self, text, parentWindow=None, title=''):
        dlg = gtk.MessageDialog(parentWindow,
                               gtk.DIALOG_MODAL,
                               gtk.MESSAGE_INFO,
                               gtk.BUTTONS_OK)
        # Dialog Title
        title = title and title or _('Information')
        dlg.set_markup(self._title_format % title)
        dlg.format_secondary_markup(text)
        dlg.run()
        dlg.destroy()
        return

    def ShowBillInfo(self, text, parentWindow=None, title=''):
        dlg = gtk.MessageDialog(parentWindow,
                               gtk.DIALOG_MODAL,
                               gtk.MESSAGE_WARNING,
                               gtk.BUTTONS_NONE)
        # Button Title
        dlg.add_button(_("Mark as paid"), gtk.RESPONSE_YES)
        dlg.add_button(_("Edit"), gtk.RESPONSE_NO)
        dlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        title = title and title or _('BillReminder')
        dlg.set_markup(self._title_format % title)
        dlg.format_secondary_markup(text)
        ret = dlg.run()
        dlg.destroy()
        return ret

    def ShowSaveConfirmation(self, parentWindow=None):
        dlg = gtk.MessageDialog(parentWindow,
                               gtk.DIALOG_MODAL,
                               gtk.MESSAGE_WARNING,
                               gtk.BUTTONS_NONE)
        dlg.add_button(_('Close _Without Saving'), gtk.RESPONSE_NO)
        dlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        dlg.add_button(gtk.STOCK_SAVE, gtk.RESPONSE_YES)

        dlg.set_default_response(gtk.RESPONSE_YES)

        dlg.set_markup(self._title_format % _('Save changes before closing?'))
        dlg.format_secondary_markup(_('If you close without saving,' \
                                      ' your changes will be discarded.'))
        ret = dlg.run()
        dlg.destroy()
        return ret

def select_combo_text(cb, text, index=0):
    """
    Searches through a gtkComoboBox for 'text' at 'index', selecting it.
    """
    i = 0
    for n in cb.get_model():
        if n[index] == text:
            break
        i += 1
    cb.set_active(i)

def str_to_date(strdate):
    dt = strdate.split()[0]
    sep = [c for c in dt if not c.isdigit()][0]
    dtPieces = [int(p) for p in dt.split(sep)]
    return datetime.date(dtPieces[0], dtPieces[1], dtPieces[2])

def force_string(dic):
    """ Force string type """
    if not isinstance(dic, dict):
        return dic
    ret = {}
    for i in range(len(dic)):
        key = dic.keys()[i]
        value = dic.values()[i]
        if not isinstance(key, basestring):
            key = str(key)
        if not isinstance(value, basestring):
            value = str(value)
        ret[key] = value
    return ret

def get_dbus_interface(interface, path):
    try:
        from dbus.mainloop.glib import DBusGMainLoop
        dbus_loop = DBusGMainLoop()
        bus = dbus.SessionBus(mainloop=dbus_loop)
        session_bus = dbus.SessionBus()
        obj = session_bus.get_object(interface, path)
        ret = dbus.Interface(obj, interface)
        return ret
    except dbus.DBusException:
        return None

def verify_dbus_service(my_interface):
    """ Verify if a specific DBus service is running """
    try:
        interface = get_dbus_interface('org.freedesktop.DBus',
                                       '/org/freedesktop/DBus')
        return my_interface in interface.ListNames()
    except dbus.DBusException:
        return False

def verify_pid(pid):
    try:
        if os.getpgid(pid):
            return True
    except OSError:
        return False

def currency_to_float(string):
    try:
        ret = locale.atof(string)
    except ValueError:
        ret = locale.atof(string.replace(
                            locale.localeconv()['mon_thousands_sep'], ''))
    return float(ret)

def float_to_currency(number):
    format = "%%.%df" % locale.localeconv()['int_frac_digits']
    ret = locale.format(format, number)
    return ret

def check_date_format(string):
    pass

def create_pixbuf(height=16, width=16, color='#F5F5F5'):

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)

    # Parse out color value
    color = gtk.gdk.color_parse(color)
    red = float(color.red) / 65536
    green = float(color.green) / 65536
    blue = float(color.blue) / 65536


    # Draw a smaller colored square inside of previous one
    cr.set_source_rgb(red, green, blue)
    cr.rectangle(0, 0, width, height)
    cr.fill ()

    # Buffer to hold the image
    buf = StringIO.StringIO()
    surface.write_to_png(buf)

    # Move pointer to start of buffer
    buf.seek(0)
    loader = gtk.gdk.PixbufLoader()
    loader.write(buf.getvalue())
    loader.close()

    return loader.get_pixbuf()
