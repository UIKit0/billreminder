#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import time
import datetime
import locale
import gobject
from subprocess import Popen
import lib.common as common
import lib.utils as utils
from lib import i18n
from lib.config import Config


class PrefDialog(gtk.Dialog):
    """
    Class used to generate dialog to allow user to edit preferences.
    """
    def __init__(self, parent=None):
        title = _("Preferences")
        gtk.Dialog.__init__(self, title=title, parent=parent, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_from_file(common.APP_ICON)
        #self.action_area.set_layout(gtk.BUTTONBOX_EDGE)

        self.props.skip_taskbar_hint = True
        self.set_border_width(5)

        self._initialize_dialog_widgets()

        if self.parent and self.parent.config:
            self.config = self.parent.config
        else:
            self.config = Config()

        self._populate_fields()
        self._connect_fields()


    def _initialize_dialog_widgets(self):
        self.topcontainer = gtk.VBox(homogeneous=False, spacing=10)

        # Startup Group
        self.startup_frame = gtk.Frame(label=_("<b>Startup</b>"))
        self.startup_frame.props.label_widget.set_use_markup(True)
        self.startup_frame.set_shadow_type(gtk.SHADOW_NONE)
        self.statup_alignment = gtk.Alignment()
        self.statup_alignment.set_padding(10, 0, 12, 0)
        self.startup_frame.add(self.statup_alignment)

        self.statup_container = gtk.VBox(homogeneous=False, spacing=6)

        self.startup_notification_checkbox = gtk.CheckButton(_("_Show notifications when user login"))

        self.startup_delay_box = gtk.HBox(homogeneous=False, spacing=0)
        self.startup_delay_label1 = gtk.Label(_("Delay: "))
        self.startup_delay_scale = gtk.HScale()
        self.startup_delay_scale.set_draw_value(False)
        self.startup_delay_scale.set_range(0, 60)
        self.startup_delay_scale.set_increments(1, 5)
        self.startup_delay_label2 = gtk.Label(_(" %s minutes") % 1)
        self.startup_delay_label2.set_size_request(100, -1)
        self.startup_delay_label2.set_alignment(0.0, 0.5)

        self.startup_minimized_checkbox = gtk.CheckButton(_("Open BillReminder _minimized in notification area"))

        self.startup_delay_box.pack_start(self.startup_delay_label1, expand=False, fill=False, padding=0)
        self.startup_delay_box.pack_start(self.startup_delay_scale, expand=True, fill=True, padding=0)
        self.startup_delay_box.pack_start(self.startup_delay_label2, expand=False, fill=False, padding=0)

        self.statup_container.pack_start(self.startup_notification_checkbox, expand=False, fill=False, padding=0)
        self.statup_container.pack_start(self.startup_delay_box, expand=False, fill=False, padding=0)
        self.statup_container.pack_start(self.startup_minimized_checkbox, expand=False, fill=False, padding=0)

        self.statup_alignment.add(self.statup_container)

        # Notification Group
        self.notification_frame = gtk.Frame(label=_("<b>Notifications</b>"))
        self.notification_frame.props.label_widget.set_use_markup(True)
        self.notification_frame.set_shadow_type(gtk.SHADOW_NONE)
        self.notification_alignment = gtk.Alignment()
        self.notification_alignment.set_padding(10, 0, 12, 0)
        self.notification_frame.add(self.notification_alignment)

        self.notification_container = gtk.VBox(homogeneous=False, spacing=6)

        self.notification_days_limit_box = gtk.HBox(homogeneous=False, spacing=0)
        self.notification_days_limit_checkbox = gtk.CheckButton(_("Show notification for bills that will be due _before "))
        self.notification_days_limit_spin = gtk.SpinButton()
        self.notification_days_limit_spin.set_range(0, 360)
        self.notification_days_limit_spin.spin(gtk.SPIN_STEP_FORWARD)
        self.notification_days_limit_spin.set_increments(1, 7)
        self.notification_days_limit_label2 = gtk.Label(_(" days"))

        self.notification_days_limit_box.pack_start(self.notification_days_limit_checkbox, expand=False, fill=False, padding=0)
        self.notification_days_limit_box.pack_start(self.notification_days_limit_spin, expand=True, fill=True, padding=0)
        self.notification_days_limit_box.pack_start(self.notification_days_limit_label2, expand=False, fill=False, padding=0)

        self.notification_alert_box = gtk.HBox(homogeneous=False, spacing=0)
        self.notification_alert_checkbox = gtk.CheckButton(_("Show _alert "))
        self.notification_alert_spin = gtk.SpinButton()
        self.notification_alert_spin.set_range(0, 360)
        self.notification_alert_spin.spin(gtk.SPIN_STEP_FORWARD)
        self.notification_alert_spin.set_increments(1, 7)
        self.notification_alert_label2 = gtk.Label(_(" days before due date, at "))
        self.notification_alert_combo = gtk.ComboBoxEntry()
        self.notification_alert_combo.child.set_width_chars(6)

        self.notification_alert_box.pack_start(self.notification_alert_checkbox, expand=False, fill=False, padding=0)
        self.notification_alert_box.pack_start(self.notification_alert_spin, expand=False, fill=True, padding=0)
        self.notification_alert_box.pack_start(self.notification_alert_label2, expand=False, fill=False, padding=0)
        self.notification_alert_box.pack_start(self.notification_alert_combo, expand=False, fill=False, padding=0)

        self.notification_due_alert_checkbox = gtk.CheckButton(_("Show alert for bills that are _due"))

        self.notification_container.pack_start(self.notification_days_limit_box, expand=False, fill=False, padding=0)
        self.notification_container.pack_start(self.notification_alert_box, expand=False, fill=False, padding=0)
        self.notification_container.pack_start(self.notification_due_alert_checkbox, expand=False, fill=False, padding=0)

        self.notification_alignment.add(self.notification_container)

        # Alert Type Group
        self.alert_frame = gtk.Frame(label=_("<b>Alert Type</b>"))
        self.alert_frame.props.label_widget.set_use_markup(True)
        self.alert_frame.set_shadow_type(gtk.SHADOW_NONE)
        self.alert_alignment = gtk.Alignment()
        self.alert_alignment.set_padding(10, 0, 12, 0)
        self.alert_frame.add(self.alert_alignment)

        self.alert_container = gtk.VBox(homogeneous=False, spacing=6)

        self.alert_box = gtk.HBox(homogeneous=False, spacing=12)
        self.alert_option1 = gtk.RadioButton(label=_("_Notification Bubble"))
        self.alert_option2 = gtk.RadioButton(group=self.alert_option1, label=_("Al_ert Dialog"))

        self.alert_box.pack_start(self.alert_option1, expand=False, fill=False, padding=0)
        self.alert_box.pack_start(self.alert_option2, expand=False, fill=False, padding=0)

        self.alert_container.pack_start(self.alert_box, expand=False, fill=False, padding=0)

        self.alert_alignment.add(self.alert_container)

        # Daemon Warning
        self.daemon_container = gtk.VBox(homogeneous=False, spacing=6)
        self.daemon_label = gtk.Label(_("<b>Warning:</b> BillReminder Daemon is not running!\nIt must be running to show notifications."))
        self.daemon_label.set_justify(gtk.JUSTIFY_CENTER)
        self.daemon_label.set_use_markup(True)
        self.daemon_image = gtk.Image()
        self.daemon_image.set_from_stock('gtk-execute', 2)
        self.daemon_button = gtk.Button(label=_("_Launch BillReminder Daemon"))
        self.daemon_button.set_image(self.daemon_image)

        self.daemon_container.pack_start(self.daemon_label, expand=False, fill=False, padding=0)
        self.daemon_container.pack_start(self.daemon_button, expand=False, fill=False, padding=0)

        # Everything
        self.topcontainer.pack_start(self.startup_frame, expand=False, fill=False, padding=0)
        self.topcontainer.pack_start(self.notification_frame, expand=False, fill=False, padding=0)
        self.topcontainer.pack_start(self.alert_frame, expand=False, fill=False, padding=0)
        if not utils.verify_dbus_service(common.DBUS_INTERFACE):
            self.topcontainer.pack_start(self.daemon_container, expand=False, fill=False, padding=0)

        self.vbox.pack_start(self.topcontainer, expand=False, fill=True, padding=10)

        self.show_all()

    def _populate_fields(self):

        self.startup_notification_checkbox.set_active(self.config.getboolean('Alarm', 'show_startup_notification'))

        delay = self.config.getint('General', 'delay')
        if delay == 0:
            msg =_(" None")
        elif delay >= 60:
            msg =_(" 1 hour")
            delay = 60
        else:
            msg = N_(" %d minute", " %d minutes", delay) % delay
        self.startup_delay_label2.set_text(msg)
        self.startup_delay_scale.set_value(delay)

        self.startup_minimized_checkbox.set_active(self.config.getboolean('General', 'start_in_tray'))

        self.notification_days_limit_checkbox.set_active(self.config.getboolean('Alarm', 'show_before_alarm'))
        self.notification_alert_checkbox.set_active(self.config.getboolean('Alarm', 'show_alarm'))
        self.notification_due_alert_checkbox.set_active(self.config.getboolean('Alarm', 'show_due_alarm'))

        if not self.config.getboolean('Alarm', 'use_alert_dialog'):
            self.alert_option1.set_active(True)
        else:
            self.alert_option2.set_active(True)

        self.notification_days_limit_spin.set_value(self.config.getint('Alarm', 'notification_days_limit'))
        self.notification_alert_spin.set_value(self.config.getint('Alarm', 'show_alarm_before_days'))

        store = gtk.ListStore(gobject.TYPE_STRING)
        for i in range(24):
            store.append(["%02d:00" % i])
            store.append(["%02d:30" % i])

        self.notification_alert_combo.set_model(store)
        self.notification_alert_combo.set_text_column(0)

        self.notification_alert_combo.child.set_text(self.config.get('Alarm', 'show_alarm_at_time'))

    def _connect_fields(self):
        self.startup_notification_checkbox.connect("toggled", self._on_checkbox_toggled, 'Alarm', 'show_startup_notification')
        self.startup_minimized_checkbox.connect("toggled", self._on_checkbox_toggled, 'General', 'start_in_tray')
        self.notification_days_limit_checkbox.connect("toggled", self._on_checkbox_toggled, 'Alarm', 'show_before_alarm')
        self.notification_alert_checkbox.connect("toggled", self._on_checkbox_toggled, 'Alarm', 'show_alarm')
        self.notification_due_alert_checkbox.connect("toggled", self._on_checkbox_toggled, 'Alarm', 'show_due_alarm')
        self.notification_alert_combo.child.connect("changed", self._on_entry_changed, 'Alarm', 'show_alarm_at_time')
        self.notification_days_limit_spin.connect("changed", self._on_entry_changed, 'Alarm', 'notification_days_limit')
        self.notification_alert_spin.connect("changed", self._on_entry_changed, 'Alarm', 'show_alarm_before_days')
        self.startup_delay_scale.connect("value-changed", self._on_scale_value_changed, 'General', 'delay')
        self.alert_option2.connect("toggled", self._on_checkbox_toggled, 'Alarm', 'use_alert_dialog')
        self.daemon_button.connect("clicked", self._launch_daemon)

    def _on_checkbox_toggled(self, togglebutton, category, item):
        self.config.set(category, item, togglebutton.get_active())
        self.config.save()

    def _on_entry_changed(self, editable, category, item):
        self.config.set(category, item, editable.get_text())
        self.config.save()

    def _on_scale_value_changed(self, range, category, item):
        delay = int(range.get_value())
        self.config.set(category, item, delay)
        self.config.save()
        if delay == 0:
            msg =_(" None")
        elif delay >= 60:
            msg =_(" 1 hour")
            delay = 60
        else:
            msg = N_(" %d minute", " %d minutes", delay) % delay
        self.startup_delay_label2.set_text(msg)

    def _launch_daemon(self, button):
        Popen('python billreminderd', shell=True)
        button.hide()
        self.daemon_label.set_markup(_("<b>Note:</b> BillReminder Daemos now is running.\nIt is needed to show notifications."))

