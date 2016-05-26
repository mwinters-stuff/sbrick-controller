import gi

gi.require_version('Gtk', '3.0')
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import Gtk
# noinspection PyUnresolvedReferences,PyPep8
from gi.repository import GObject


class SBrickInfoBox(Gtk.Frame):
    def __init__(self):
        Gtk.Frame.__init__(self)
        self.sbrick = None
        self.set_label("SBrick Information")

        self.store = Gtk.ListStore(str, str)
        self.iterSBrickID = self.store.append(["SBrick BlueGiga ID", "--"])
        self.iterHardwareVersion = self.store.append(["Hardware Version", "--"])
        self.iterSoftwareVersion = self.store.append(["Software Version", "--"])
        self.iterNeedAuthentication = self.store.append(["Need Authentication", "--"])
        self.iterIsAuthenticated = self.store.append(["Is Authenticated", "--"])
        self.iterAuthenticationTimeout = self.store.append(["Authentication Timeout", "--"])
        self.iterInputVoltage = self.store.append(["Input Voltage", "--"])
        self.iterTemperature = self.store.append(["Temperature", "--"])
        self.iterPowerCycles = self.store.append(["Power Cycles", "--"])
        self.iterWatchdogTimeout = self.store.append(["Watchdog Timeout", "--"])
        self.iterUpTime = self.store.append(["Up Time", "--"])
        self.iterThermalLimit = self.store.append(["Thermal Limit", "--"])

        self.listView = Gtk.TreeView(self.store)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Item", renderer, text=0)
        self.listView.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Value", renderer, text=1)
        self.listView.append_column(column)

        self.scrollTree = Gtk.ScrolledWindow()
        self.scrollTree.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrollTree.add(self.listView)

        self.add(self.scrollTree)
        self.set_sensitive(False)

    def set_sbrick(self, sbrick):
        self.sbrick = sbrick
        self.set_sensitive(sbrick is not None)
        if sbrick is not None:
            self.refresh_all_values()
            GObject.timeout_add_seconds(5, self.refresh_updating_values)

    def refresh_all_values(self):
        self.refresh_updating_values()
        self.refresh_once_values()

    def refresh_updating_values(self):
        if self.sbrick is not None:
            # print ("timer")
            self.store[self.iterInputVoltage][1] = self.none_or_value("%0.2f", self.sbrick.get_voltage())
            self.store[self.iterTemperature][1] = self.none_or_value("%0.2f", self.sbrick.get_temperature())
            self.store[self.iterUpTime][1] = self.none_or_value("%s", self.sbrick.get_uptime())
            return True
        return False

    def refresh_once_values(self):
        if self.sbrick is not None:
            self.store[self.iterSBrickID][1] = self.none_or_value("%s", self.sbrick.get_brick_id())
            self.store[self.iterHardwareVersion][1] = self.none_or_value("%s", self.sbrick.get_hardware_version())
            self.store[self.iterSoftwareVersion][1] = self.none_or_value("%s", self.sbrick.get_software_version())
            self.store[self.iterPowerCycles][1] = self.none_or_value("%d", self.sbrick.get_power_cycle_counter())
            self.store[self.iterWatchdogTimeout][1] = self.none_or_value("%0.2f", self.sbrick.get_watchdog_timeout())
            self.store[self.iterThermalLimit][1] = self.none_or_value("%0.2f", self.sbrick.get_thermal_limit())
            self.store[self.iterNeedAuthentication][
                1] = "%s" % 'Yes' if self.sbrick.get_need_authentication() == True else 'No'
            self.store[self.iterIsAuthenticated][1] = "%s" % 'Yes' \
                if self.sbrick.get_is_authenticated() == True else 'No'
            self.store[self.iterAuthenticationTimeout][1] = self.none_or_value("%0.2f",
                                                                               self.sbrick.get_authentication_timeout())

    @staticmethod
    def none_or_value(formatstr, value):
        if value is None:
            return '--'
        return formatstr % value
