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
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file(common.APP_ICON)
        self.action_area.set_layout(gtk.BUTTONBOX_EDGE)

        self.props.skip_taskbar_hint = True
        self.set_border_width(5)

        self._initialize_dialog_widgets()


    def _initialize_dialog_widgets(self):
        self.topcontainer = gtk.VBox(homogeneous=False, spacing=10)

        # Frames
        self.startup_frame = gtk.Frame(label=_("<b>Startup</b>"))
        self.notification_frame = gtk.Frame(label=_("<b>Notifications</b>"))
        self.alert_frame = gtk.Frame(label=_("<b>Alert Type</b>"))

        self.startup_frame.props.label_widget.set_use_markup(True)
        self.notification_frame.props.label_widget.set_use_markup(True)
        self.alert_frame.props.label_widget.set_use_markup(True)
        self.startup_frame.set_shadow_type(gtk.SHADOW_NONE)
        self.notification_frame.set_shadow_type(gtk.SHADOW_NONE)
        self.alert_frame.set_shadow_type(gtk.SHADOW_NONE)
        self.daemon_warning = gtk.VBox(homogeneous=False, spacing=6)

        self.statup_alignment = gtk.Alignment()
        self.statup_alignment.set_padding(10, 0, 12, 0)
        self.statup_container = gtk.VBox(homogeneous=False, spacing=6)

        self.startup_notification_checkbox = gtk.CheckButton(_("Show notifications when user login"))

        self.startup_delay_box = gtk.HBox(homogeneous=False, spacing=0)
        self.startup_delay_label1 = gtk.Label(_("Delay: "))
        self.startup_delay_scale = gtk.HScale()
        self.startup_delay_scale.set_draw_value(False)
        self.startup_delay_label2 = gtk.Label(_(" %s minutes") % 1)

        self.startup_minimized_checkbox = gtk.CheckButton(_("Open BillReminder minimized in notification area"))

        self.startup_delay_box.pack_start(self.startup_delay_label1, expand=False, fill=False, padding=0)
        self.startup_delay_box.pack_start(self.startup_delay_scale, expand=True, fill=True, padding=0)
        self.startup_delay_box.pack_start(self.startup_delay_label2, expand=False, fill=False, padding=0)

        self.notification_alignment = gtk.Alignment()
        self.notification_alignment.set_padding(10, 0, 12, 0)
        self.notification_container = gtk.VBox(homogeneous=False, spacing=6)

        self.notification_days_limit_box = gtk.HBox(homogeneous=False, spacing=0)
        self.notification_days_limit_checkbox = gtk.CheckButton(_("Show notification for bills that will be due before "))
        self.notification_days_limit_spin = gtk.SpinButton()
        self.notification_days_limit_label2 = gtk.Label(_(" days"))

        self.notification_days_limit_box.pack_start(self.notification_days_limit_checkbox, expand=False, fill=False, padding=0)
        self.notification_days_limit_box.pack_start(self.notification_days_limit_spin, expand=True, fill=True, padding=0)
        self.notification_days_limit_box.pack_start(self.notification_days_limit_label2, expand=False, fill=False, padding=0)

        self.notification_alert_box = gtk.HBox(homogeneous=False, spacing=0)
        self.notification_alert_checkbox = gtk.CheckButton(_("Show alert "))
        self.notification_alert_spin = gtk.SpinButton()
        self.notification_alert_label2 = gtk.Label(_(" days before due date, at "))
        self.notification_alert_combo = gtk.ComboBoxEntry()
        self.notification_alert_combo.child.set_width_chars(6)

        self.notification_alert_box.pack_start(self.notification_alert_checkbox, expand=False, fill=False, padding=0)
        self.notification_alert_box.pack_start(self.notification_alert_spin, expand=False, fill=True, padding=0)
        self.notification_alert_box.pack_start(self.notification_alert_label2, expand=False, fill=False, padding=0)
        self.notification_alert_box.pack_start(self.notification_alert_combo, expand=False, fill=False, padding=0)

        self.notification_due_alert_checkbox = gtk.CheckButton(_("Show alert for bills that are due"))

        self.alert_alignment = gtk.Alignment()
        self.alert_alignment.set_padding(10, 0, 12, 0)
        self.alert_container = gtk.VBox(homogeneous=False, spacing=6)

        self.alert_box = gtk.HBox(homogeneous=False, spacing=12)
        self.alert_option1 = gtk.RadioButton(label=_("Notification Bubble"))
        self.alert_option2 = gtk.RadioButton(group=self.alert_option1, label=_("Alert Dialog"))

        self.alert_box.pack_start(self.alert_option1, expand=False, fill=False, padding=0)
        self.alert_box.pack_start(self.alert_option2, expand=False, fill=False, padding=0)

        self.daemon_container = gtk.VBox(homogeneous=False, spacing=6)
        self.daemon_label = gtk.Label(_("BillReminder Daemon is not running!\nIt must be running to show notifications."))
        self.daemon_label.set_justify(gtk.JUSTIFY_CENTER)
        self.daemon_button = gtk.Button(label=_("Launch BillReminder Daemon"))

        # Everything
        self.statup_container.pack_start(self.startup_notification_checkbox, expand=False, fill=False, padding=0)
        self.statup_container.pack_start(self.startup_delay_box, expand=False, fill=False, padding=0)
        self.statup_container.pack_start(self.startup_minimized_checkbox, expand=False, fill=False, padding=0)

        self.notification_container.pack_start(self.notification_days_limit_box, expand=False, fill=False, padding=0)
        self.notification_container.pack_start(self.notification_alert_box, expand=False, fill=False, padding=0)
        self.notification_container.pack_start(self.notification_due_alert_checkbox, expand=False, fill=False, padding=0)

        self.alert_container.pack_start(self.alert_box, expand=False, fill=False, padding=0)

        self.daemon_container.pack_start(self.daemon_label, expand=False, fill=False, padding=0)
        self.daemon_container.pack_start(self.daemon_button, expand=False, fill=False, padding=0)

        self.statup_alignment.add(self.statup_container)
        self.notification_alignment.add(self.notification_container)
        self.alert_alignment.add(self.alert_container)

        self.startup_frame.add(self.statup_alignment)
        self.notification_frame.add(self.notification_alignment)
        self.alert_frame.add(self.alert_alignment)

        self.topcontainer.pack_start(self.startup_frame, expand=False, fill=False, padding=0)
        self.topcontainer.pack_start(self.notification_frame, expand=False, fill=False, padding=0)
        self.topcontainer.pack_start(self.alert_frame, expand=False, fill=False, padding=0)
        # TODO: Pack only if daemon is not running
        self.topcontainer.pack_start(self.daemon_container, expand=False, fill=False, padding=0)
        self.vbox.pack_start(self.topcontainer, expand=False, fill=True, padding=10)

        self.show_all()
