# OLED BT KB PAGE
#     Should show the user if a pi-top BT KB is detected
#         For now, continously poll lsusb when page is in view
#             When found, confirm BT Mac address in /proc/bus/input/devices

# Settings pages - set them as static, but allow each page to update to dbus events
#     systemd services (if possible)
#           https://trstringer.com/python-systemd-dbus/

#     Bluetooth/USB state change
#           https://stackoverflow.com/questions/5109879/usb-devices-udev-and-d-bus#5111493

#     Do nothing if not
#     Update the page to "in progress" state for connection; disable navigation until complete (include timeout)
#         clearly communicate "Please press Bluetooth button on your keyboard to auto pair..." visually

#     for auto pairing, use pt-bt-kb stuff from ptdm


from pitopcommon.logger import PTLogger

from dbus import (
    exceptions,
    Boolean,
    Interface,
    SystemBus,
)
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository.GObject import MainLoop
from subprocess import getoutput
from threading import (
    Thread,
    Event,
)
from time import sleep


SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"

DBusGMainLoop(set_as_default=True)
bus = SystemBus()


def on_bt_scan_finished():
    pass


def on_bt_remove_finished():
    pass


def on_bt_pair_change_finished():
    pass


def on_bt_connect_finished():
    pass


def on_bt_disconnect_finished():
    pass


def on_bt_trust_change_finished():
    pass


def on_bt_block_change_finished():
    pass


def on_failed_to_connect_bt_keyboard():
    pass


def on_successful_connect_bt_keyboard():
    pass


def get_keyboard_last_master_mac_address():
    pass


def trigger_keyboard_pairing_mode():
    pass


def get_keyboard_mac_address():
    # TODO: get BT KB mac address in /proc/bus/input/devices
    pass


def on_bt_connection_detected():
    pass


def on_bt_disconnection_detected():
    pass


def mac_addr_int_to_str(mac_addr_int: int):
    bt_addr_hex = "{:012x}".format(mac_addr_int)
    return ":".join(
        bt_addr_hex[i: i + 2] for i in range(0, len(bt_addr_hex), 2)
    ).lower()


def get_current_bt_interface_address():
    cmd = "hciconfig"
    device_id = "hci0"
    bt_mac = (
        getoutput(cmd)
        .split("{}:".format(device_id))[1]
        .split("BD Address: ")[1]
        .split(" ")[0]
        .strip()
    )
    return bt_mac.lower()


class BluezException(Exception):
    pass


class BluezNoAdapterException(BluezException):
    pass


class BluezNoDeviceException(BluezException):
    pass


class AdapterHelper:
    @staticmethod
    def get_list():
        adapter_path = BluezUtils.find_adapter().object_path

        om = Interface(
            bus.get_object(
                SERVICE_NAME, "/"), "org.freedesktop.DBus.ObjectManager"
        )
        objects = om.GetManagedObjects()

        parsed_objects = list()

        for obj_path, interfaces in objects.items():
            if DEVICE_INTERFACE not in interfaces:
                continue
            properties = interfaces[DEVICE_INTERFACE]
            if properties["Adapter"] != adapter_path:
                continue
            parsed_objects.append(properties)

        return parsed_objects


class BluezUtils:
    @staticmethod
    def get_managed_objects():
        manager = Interface(
            bus.get_object(
                SERVICE_NAME, "/"), "org.freedesktop.DBus.ObjectManager"
        )
        return manager.GetManagedObjects()

    @staticmethod
    def find_adapter(pattern=None):
        return BluezUtils.find_adapter_in_objects(
            BluezUtils.get_managed_objects(), pattern
        )

    @staticmethod
    def find_adapter_in_objects(objects, pattern=None):
        for path, ifaces in objects.items():
            adapter = ifaces.get(ADAPTER_INTERFACE)
            if adapter is None:
                continue
            if not pattern or pattern == adapter["Address"] or path.endswith(pattern):
                obj = bus.get_object(SERVICE_NAME, path)
                return Interface(obj, ADAPTER_INTERFACE)
        raise BluezNoAdapterException("Bluez: No adapter found")

    @staticmethod
    def find_device(device_address, adapter_pattern=None):
        return BluezUtils.find_device_in_objects(
            BluezUtils.get_managed_objects(), device_address, adapter_pattern
        )

    @staticmethod
    def find_device_in_objects(objects, device_address, adapter_pattern=None):
        path_prefix = ""
        if adapter_pattern:
            adapter = BluezUtils.find_adapter_in_objects(
                objects, adapter_pattern)
            path_prefix = adapter.object_path
        for path, ifaces in objects.items():
            device = ifaces.get(DEVICE_INTERFACE)
            if device is None:
                continue
            if device["Address"] is None:
                continue
            if device["Address"].lower() == device_address.lower() and path.startswith(path_prefix):
                obj = bus.get_object(SERVICE_NAME, path)
                return Interface(obj, DEVICE_INTERFACE)

        raise BluezNoDeviceException(
            "Bluez: No device found matching %s", device_address
        )


class DeviceHelper:
    @staticmethod
    def _get_path_from_device(device):
        return device.object_path

    @staticmethod
    def _get_props_from_path(device_path):
        return Interface(
            bus.get_object(
                SERVICE_NAME, device_path), "org.freedesktop.DBus.Properties"
        )

    @staticmethod
    def get_device(mac_address):
        return BluezUtils.find_device(mac_address)

    @staticmethod
    def get_device_path(mac_address):
        return DeviceHelper._get_path_from_device(DeviceHelper.get_device(mac_address))

    @staticmethod
    def get_device_props(mac_address):
        return DeviceHelper._get_props_from_path(
            DeviceHelper.get_device_path(mac_address)
        )


# TODO: Initial starting scan needs to be threaded - currently not returning results
# TODO: Only use mainloop.run() in threaded event handler
# TODO: Always listen for {dis}connections

# Adapted from:
#       https://github.com/pauloborges/bluez/blob/master/test/monitor-bluetooth
#       https://github.com/pauloborges/bluez/blob/master/test/test-device
#       https://github.com/pauloborges/bluez/blob/master/test/test-discovery


class BTManager:
    def __init__(self):
        self._thread = Thread(target=self._thread_method)
        self._continue = False
        self._mainloop = MainLoop()
        self._bus = SystemBus()

    def _set_up_signals(self):
        def interfaces_added(path, interfaces):
            # TODO: Check if it is an interface we care about; process accordingly
            for iface, props in interfaces.items():
                if not (iface in [ADAPTER_INTERFACE, DEVICE_INTERFACE]):
                    continue
                PTLogger.debug(
                    "Path [%s] added to interface {%s}" % (path, iface))
                for name, value in props.items():
                    PTLogger.debug("      %s = %s" % (name, value))

        def interfaces_removed(path, interfaces):
            # TODO: Check if it is an interface we care about; process accordingly
            for iface in interfaces:
                if not (iface in [ADAPTER_INTERFACE, DEVICE_INTERFACE]):
                    continue
                PTLogger.debug(
                    "Path [%s] removed from interface {%s}" % (path, iface))

        def disc_completed_signal(name, value):
            # TODO: This is not yet working
            PTLogger.info("BTManager: Discovery Completed")
            self._mainloop.quit()
            on_bt_scan_finished()

        self._bus.add_signal_receiver(
            interfaces_added,
            bus_name="org.bluez",
            dbus_interface="org.freedesktop.DBus.ObjectManager",
            signal_name="InterfacesAdded",
        )

        self._bus.add_signal_receiver(
            interfaces_removed,
            bus_name="org.bluez",
            dbus_interface="org.freedesktop.DBus.ObjectManager",
            signal_name="InterfacesRemoved",
        )

        self._bus.add_signal_receiver(
            disc_completed_signal,
            bus_name="org.bluez",
            dbus_interface="org.freedesktop.DBus.ObjectManager",
            signal_name="DiscoveryCompleted",
        )

    def initialise(self):
        # self._set_up_signals()
        pass

    def start(self):
        self._continue = True
        self._thread.start()

    def stop(self):
        PTLogger.info("Stopping Bluetooth manager...")

        if self._thread.is_alive():
            self._continue = False
            self._mainloop.quit()
            self._thread.join()

        PTLogger.debug("Bluetooth manager stopped.")

    def _thread_method(self):
        while self._continue:
            try:
                PTLogger.info("Starting Bluetooth manager...")

                if self._continue is True:
                    PTLogger.info("Running Bluetooth signal monitor...")
                    self._mainloop.run()

                BTManager.stop_discovery()
            except Exception as e:
                PTLogger.info(
                    "Bluetooth manager thread encountered an error...")
                PTLogger.warning(e)

    @staticmethod
    def start_discovery():
        PTLogger.info("Starting Bluetooth discovery...")
        try:
            adapter = BluezUtils.find_adapter()
            adapter.StartDiscovery()
            return True
        except exceptions.DBusException as e:
            PTLogger.warning("Failed to start Bluetooth discovery")
            PTLogger.warning("DBus Exception: " + e.get_dbus_message())

        return False

    @staticmethod
    def stop_discovery():
        PTLogger.info("Stopping Bluetooth discovery...")
        try:
            adapter = BluezUtils.find_adapter()
            adapter.StopDiscovery()
            return True
        except exceptions.DBusException as e:
            PTLogger.warning("Failed to stop Bluetooth discovery")
            PTLogger.warning("DBus Exception: " + e.get_dbus_message())

        return False

    @staticmethod
    def list():
        return AdapterHelper.get_list()

    def is_found(self, mac_address):
        found = False
        PTLogger.info(
            "Attempting to determine found status of BT device with mac address "
            + mac_address
        )
        try:
            found = DeviceHelper.get_device(mac_address)
        except BluezNoDeviceException:
            # Device is not known about
            pass

        if found:
            PTLogger.info("BT device with mac address " +
                          mac_address + " was found")
        else:
            PTLogger.info(
                "BT device with mac address " + mac_address + " could not be found"
            )

        return found

    def remove(self, mac_address):
        PTLogger.info(
            "Attempting to remove BT device with mac address " + mac_address)
        try:
            BluezUtils.find_adapter().RemoveDevice(
                BluezUtils.find_device_in_objects(
                    BluezUtils.get_managed_objects(), mac_address
                ).object_path
            )
        except BluezNoDeviceException:
            PTLogger.warning(
                "Warning: trying to remove "
                + str(mac_address)
                + ", but no matching Bluez device found"
            )

        on_bt_remove_finished(mac_address)

    def pair(self, mac_address):
        PTLogger.info(
            "Attempting to pair BT device with mac address " + mac_address)
        if not self.is_paired(mac_address):
            try:
                DeviceHelper.get_device(mac_address).Pair()
            except exceptions.DBusException as e:
                PTLogger.warning("DBus Exception: " + e.get_dbus_message())
                PTLogger.warning(
                    "Error: unable to pair with " + str(mac_address))
                return

            on_bt_pair_change_finished(mac_address, True)

    def is_paired(self, mac_address):
        PTLogger.info(
            "Attempting to determine paired status of BT device with mac address "
            + mac_address
        )
        paired = False
        try:
            paired = (
                DeviceHelper.get_device_props(mac_address).Get(
                    DEVICE_INTERFACE, "Paired"
                )
                == 1
            )
        except BluezNoDeviceException:
            # Device is not known about - leave as false
            PTLogger.warning(
                "Warning: trying to check if "
                + str(mac_address)
                + " is paired, but no matching Bluez device found"
            )

        return paired

    def connect(self, mac_address, profile=None):
        PTLogger.info(
            "Attempting to connect to BT device with mac address " + mac_address
        )
        if profile is not None:
            try:
                DeviceHelper.get_device(mac_address).ConnectProfile(profile)
            except exceptions.DBusException as e:
                PTLogger.warning(
                    "Error: unable to connect with profile with " +
                    str(mac_address)
                )
                PTLogger.warning("DBus Exception: " + e.get_dbus_message())
                return
        else:
            try:
                DeviceHelper.get_device(mac_address).Connect()
            except exceptions.DBusException as e:
                PTLogger.warning(
                    "Error: unable to connect to " + str(mac_address))
                PTLogger.warning("DBus Exception: " + e.get_dbus_message())
                return

        on_bt_connect_finished(mac_address)

    def disconnect(self, mac_address, profile=None):
        PTLogger.info(
            "Attempting to disconnect to BT device with mac address " + mac_address
        )
        if profile is not None:
            try:
                DeviceHelper.get_device(mac_address).DisconnectProfile(profile)
            except exceptions.DBusException as e:
                PTLogger.warning(
                    "Error: unable to disconnect with profile with " +
                    str(mac_address)
                )
                PTLogger.warning("DBus Exception: " + e.get_dbus_message())
                return
        else:
            try:
                DeviceHelper.get_device(mac_address).Disconnect()
            except exceptions.DBusException as e:
                PTLogger.warning(
                    "Error: unable to disconnect to " + str(mac_address))
                PTLogger.warning("DBus Exception: " + e.get_dbus_message())
                return

        on_bt_disconnect_finished(mac_address)

    def is_connected(self, mac_address):
        PTLogger.info(
            "Attempting to determine connection status of BT device with mac address "
            + mac_address
        )
        connected = False
        try:
            connected = (
                DeviceHelper.get_device_props(mac_address).Get(
                    DEVICE_INTERFACE, "Connected"
                )
                == 1
            )
        except BluezNoDeviceException:
            # Device is not known about - leave as false
            PTLogger.warning(
                "Warning: trying to check if "
                + str(mac_address)
                + " is connected, but no matching Bluez device found"
            )

        return connected

    def trust(self, mac_address, trust=True):
        PTLogger.info(
            "Attempting to trust BT device with mac address " + mac_address)
        DeviceHelper.get_device_props(mac_address).Set(
            DEVICE_INTERFACE, "Trusted", Boolean(1) if trust else Boolean(0)
        )
        on_bt_trust_change_finished(mac_address, trust)

    def is_trusted(self, mac_address):
        PTLogger.info(
            "Attempting to determine trust status of BT device with mac address "
            + mac_address
        )
        trusted = False
        try:
            trusted = (
                DeviceHelper.get_device_props(mac_address).Get(
                    DEVICE_INTERFACE, "Trusted"
                )
                == 1
            )
        except BluezNoDeviceException:
            # Device is not known about - leave as false
            PTLogger.warning(
                "Warning: trying to check if "
                + str(mac_address)
                + " is trusted, but no matching Bluez device found"
            )

        return trusted

    def block(self, mac_address, block=True):
        PTLogger.info(
            "Attempting to block BT device with mac address " + mac_address)
        DeviceHelper.get_device_props(mac_address).Set(
            DEVICE_INTERFACE, "Blocked", Boolean(1) if block else Boolean(0)
        )
        on_bt_block_change_finished(mac_address, block)

    def is_blocked(self, mac_address):
        PTLogger.info(
            "Attempting to determine block status of BT device with mac address "
            + mac_address
        )
        blocked = False
        try:
            blocked = (
                DeviceHelper.get_device_props(mac_address).Get(
                    DEVICE_INTERFACE, "Blocked"
                )
                == 1
            )
        except BluezNoDeviceException:
            # Device is not known about - leave as false
            PTLogger.warning(
                "Warning: trying to check if "
                + str(mac_address)
                + " is blocked, but no matching Bluez device found"
            )

        return blocked


class BTKBManager:
    def __init__(self):
        self._auto_connect_thread = Thread(
            target=self._auto_connect_thread_method)
        self._thread_start_event = Event()
        self._continue = False
        self._keyboard_mac_address = ""
        self.trying_to_connect = False
        self.trying_to_identify = False
        self._bt_manager = BTManager()

    def initialise(self):
        self._bt_manager.initialise()
        self._set_up_kb_signals()

    def start(self):
        PTLogger.info("Starting Bluetooth keyboard manager...")
        self._bt_manager.start()
        self._continue = True
        self._auto_connect_thread.start()

    def stop(self):
        PTLogger.info("Stopping Bluetooth keyboard manager...")
        if self._auto_connect_thread.is_alive():
            self._continue = False
            self._thread_start_event.set()
            PTLogger.info("Waiting for auto connect thread to finish...")
            self._auto_connect_thread.join()
        PTLogger.debug("Stopping BT Manager")
        self._bt_manager.stop()
        PTLogger.debug("Stopped Bluetooth keyboard manager...")

    def signal_auto_connect(self):

        # If the thread is already running, stop any in progress
        # identification or connection

        self.cleanup_connect_bt_keyboard()

        # Set the event, so that the thread will start the
        # auto connect process (or re-start it if is already
        # running)
        self._thread_start_event.set()

    def _auto_connect_thread_method(self):
        PTLogger.info("Starting keyboard auto connect thread...")
        while self._continue:
            try:
                PTLogger.info(
                    "Thread waiting for next signal to start keyboard auto connect routine..."
                )
                # Wait until we are signalled by the event being set (or if the
                # event was set before we were waiting)
                self._thread_start_event.wait()
                self._thread_start_event.clear()

                PTLogger.info("Starting keyboard auto connect procedure...")
                if self._continue is True:

                    if self.determine_current_keyboard_mac_address():

                        # self.disconnect_bt_keyboard_if_connected()
                        self.attempt_auto_connect()

                        PTLogger.info(
                            "Keyboard auto connection process complete")
                    else:

                        PTLogger.warning(
                            "Failed to determine pi-top Bluetooth keyboard mac address"
                        )

                        on_failed_to_connect_bt_keyboard()

            except Exception as e:
                PTLogger.info(
                    "Keyboard autoconnect thread encountered an error...")
                PTLogger.warning(e)

    def attempt_auto_connect(self):
        PTLogger.info(
            "Attempting to auto connect with pi-top Bluetooth keyboard")

        self.trying_to_connect = True

        PTLogger.info("Checking if Bluetooth keyboard needs to be paired with")

        is_found = self.is_found()
        attempt_to_pair = not is_found

        if is_found:
            PTLogger.info("Record found for Bluetooth keyboard")
            is_paired = self.is_paired()
            PTLogger.info("Is BT keyboard paired? " + str(is_paired))

            is_master_of_keyboard = self.is_master_of_keyboard()

            if is_paired and is_master_of_keyboard:
                PTLogger.info(
                    "Paired with this device, and acknowledged as master of keyboard - nothing to do"
                )
                self.trying_to_connect = False
                return

            if is_paired and not is_master_of_keyboard:
                PTLogger.info(
                    "Not master of pi-top Bluetooth keyboard - forgetting previous keyboards"
                )
                self.forget_all_bt_keyboards()
                is_paired = False
                PTLogger.info("Is BT keyboard paired? " + str(is_paired))

            attempt_to_pair = not is_paired
        else:
            PTLogger.info(
                "No record found for pi-top Bluetooth keyboard - forgetting all record of previous keyboards"
            )
            self.forget_all_bt_keyboards()

        if not self.trying_to_connect:
            PTLogger.warning(
                "No longer trying to connect to keyboard - abandoning auto connect"
            )
            return

        if attempt_to_pair:
            if not BTManager.start_discovery():
                PTLogger.warning(
                    "Unable to start Bluetooth discovery - "
                    "abandoning attempt to pair automatically"
                )
                on_failed_to_connect_bt_keyboard()
                return

        if attempt_to_pair:
            self.attempt_to_pair_bt_kb()

        if not self.is_paired():
            PTLogger.warning(
                "Unable to pair with pi-top Bluetooth keyboard - "
                "abandoning attempt to pair automatically"
            )
            on_failed_to_connect_bt_keyboard()
            return

        self.attempt_to_unblock_bt_kb()
        if self.is_blocked():
            PTLogger.warning("Unable to unblock BT keyboard...")
            on_failed_to_connect_bt_keyboard()
            return

        self.attempt_to_trust_bt_kb()
        if not self.is_trusted():
            PTLogger.warning("Unable to trust BT keyboard...")
            on_failed_to_connect_bt_keyboard()
            return

        # Force disconnect before trying to connect
        if self.is_connected():
            self.disconnect()

        self.attempt_to_connect_bt_kb()
        if not self.is_connected():
            PTLogger.warning("Unable to connect to BT keyboard...")
            on_failed_to_connect_bt_keyboard()
            return

        on_successful_connect_bt_keyboard()

    def is_master_of_keyboard(self):
        keyboard_last_master_mac_addr = (
            get_keyboard_last_master_mac_address()
        )

        if keyboard_last_master_mac_addr is None or keyboard_last_master_mac_addr == "":
            PTLogger.warning(
                "Unable to get keyboard's last master mac address")
            return False

        last_master_addr = mac_addr_int_to_str(
            get_keyboard_last_master_mac_address()
        )

        current_addr = get_current_bt_interface_address()

        PTLogger.info("Keyboard's last BT master addr: " + last_master_addr)
        PTLogger.info("Current BT interface addr: " + current_addr)

        return last_master_addr == current_addr

    def forget_all_bt_keyboards(self):
        for bt_object in BTManager.list():
            if bt_object.get("Modalias", None) == "usb:v04E8p7021d0001":
                addr = bt_object.get("Address", None)
                if addr is not None:
                    PTLogger.info(
                        "pi-top keyboard detected - forgetting " + addr + "..."
                    )
                    if self._bt_manager.is_connected(addr):
                        PTLogger.info(
                            "Previous pi-top keyboard is currently connected via Bluetooth - disconnecting..."
                        )
                        self._bt_manager.disconnect(addr)
                    self._bt_manager.remove(addr)

    def attempt_to_pair_bt_kb(self):
        PTLogger.info("Attempting to pair with Bluetooth keyboard")
        PTLogger.info("Triggering BT keyboard pairing mode...")

        trigger_keyboard_pairing_mode()

        if self.wait_until_kb_found(max_no_attempts=20, interval=1):
            PTLogger.info("Attempting to pair with BT keyboard...")
            self.pair()
        else:
            PTLogger.warning(
                "Unable to find pi-top Bluetooth keyboard after waiting")

    def attempt_to_unblock_bt_kb(self):
        PTLogger.info("Is BT keyboard unblocked? " +
                      str(not self.is_blocked()))
        if self.is_blocked():
            PTLogger.debug("Unblocking BT keyboard...")
            self.block(False)

    def attempt_to_trust_bt_kb(self):
        PTLogger.info("Is BT keyboard trusted? " + str(self.is_trusted()))
        if not self.is_trusted():
            PTLogger.debug("Trusting BT keyboard...")
            self.trust()

    def attempt_to_connect_bt_kb(self):
        PTLogger.info("Is BT keyboard connected? " + str(self.is_connected()))
        if not self.is_connected():
            PTLogger.debug("Connecting to BT keyboard...")
            self.connect()

    def cleanup_connect_bt_keyboard(self):
        self.trying_to_identify = False
        self.trying_to_connect = False
        self.clear_keyboard_mac_address()
        BTManager.stop_discovery()

    def wait_until_kb_found(self, max_no_attempts=20, interval=1):
        is_found = self.is_found()
        if not is_found:
            PTLogger.info("BT keyboard not yet found - waiting to find it")
            counter = 0

            while self.trying_to_connect and counter < max_no_attempts:
                counter += 1

                PTLogger.info(
                    "Attempt number " + str(counter) +
                    "/" + str(max_no_attempts)
                )

                is_found = self.is_found()

                if is_found:
                    PTLogger.info("Found BT keyboard")
                else:
                    PTLogger.info("Not yet found BT keyboard")

                if is_found:
                    break
                elif counter < max_no_attempts:
                    sleep(interval)

        if not self.trying_to_connect:
            PTLogger.warning(
                "No longer trying to connect to keyboard - abandoning attempt to find keyboard"
            )

        return self.is_found()

    def determine_current_keyboard_mac_address(self):
        PTLogger.info(
            "About to attempt to determine current keyboard's mac address")
        counter = 0
        max_no_attempts = 20
        device_bt_addr = None

        def device_bt_addr_is_defined(bt_addr):
            return bt_addr != 0 and bt_addr is not None

        self.trying_to_identify = True

        while self.trying_to_identify and counter < max_no_attempts:
            counter += 1

            PTLogger.info(
                "Attempting to determine current keyboard's mac address - "
                + str(counter)
                + "/"
                + str(max_no_attempts)
            )
            device_bt_addr = get_keyboard_mac_address()
            if device_bt_addr_is_defined(device_bt_addr):
                PTLogger.info("Current keyboard's mac address determined")
            else:
                PTLogger.info(
                    "Current keyboard's mac address not yet determined")

            if device_bt_addr_is_defined(device_bt_addr):
                break
            elif counter < max_no_attempts:
                sleep(1)

        self.trying_to_identify = False

        if not device_bt_addr_is_defined(device_bt_addr):
            PTLogger.warning(
                "Unable to determine current keyboard's mac address")
            return False

        self.set_keyboard_mac_address(device_bt_addr)
        return True

    def disconnect_bt_keyboard_if_connected(self):
        PTLogger.info("Attempting to disconnect from keyboard if connected...")
        is_found = self.is_found()
        if is_found:
            PTLogger.info("Record found for Bluetooth keyboard")
            is_connected = self.is_connected()
            PTLogger.info("Is BT keyboard connected? " + str(is_connected))
            if is_connected:
                PTLogger.info("Disconnecting from BT keyboard")
                self.disconnect()

    def set_keyboard_mac_address(self, keyboard_mac_address: int):
        self._keyboard_mac_address = mac_addr_int_to_str(keyboard_mac_address)
        PTLogger.info(
            "Setting local copy of pi-top Bluetooth keyboard mac address: "
            + str(self._keyboard_mac_address)
        )

    def clear_keyboard_mac_address(self):
        PTLogger.info(
            "Clearing local copy of pi-top Bluetooth keyboard mac address")
        self._keyboard_mac_address = ""

    def pair(self):
        if self._keyboard_mac_address == "":
            PTLogger.warning(
                "Trying to pair with undefined Bluetooth keyboard")
            return
        self._bt_manager.pair(self._keyboard_mac_address)

    def is_paired(self):
        return self._bt_manager.is_paired(self._keyboard_mac_address)

    def is_found(self):
        return self._bt_manager.is_found(self._keyboard_mac_address)

    def remove(self, profile=None):
        if self._keyboard_mac_address == "":
            PTLogger.warning("Trying to remove undefined Bluetooth keyboard")
            return
        # TODO: what is 'profile' - not an argument on remove
        self._bt_manager.remove(self._keyboard_mac_address, profile)

    def connect(self, profile=None):
        if self._keyboard_mac_address == "":
            PTLogger.warning(
                "Trying to connect with undefined Bluetooth keyboard")
            return
        self._bt_manager.connect(self._keyboard_mac_address, profile)

    def disconnect(self, profile=None):
        if self._keyboard_mac_address == "":
            PTLogger.warning(
                "Trying to disconnect with undefined Bluetooth keyboard")
            return
        self._bt_manager.disconnect(self._keyboard_mac_address, profile)

    def is_connected(self):
        return self._bt_manager.is_connected(self._keyboard_mac_address)

    def trust(self, trust=True):
        if self._keyboard_mac_address == "":
            PTLogger.warning(
                "Trying to change trusted state of undefined Bluetooth keyboard"
            )
            return
        self._bt_manager.trust(self._keyboard_mac_address, trust)

    def is_trusted(self):
        return self._bt_manager.is_trusted(self._keyboard_mac_address)

    def block(self, block=True):
        if self._keyboard_mac_address == "":
            PTLogger.warning(
                "Trying to change blocked state of undefined Bluetooth keyboard"
            )
            return
        self._bt_manager.block(self._keyboard_mac_address, block)

    def is_blocked(self):
        return self._bt_manager.is_blocked(self._keyboard_mac_address)

    def _set_up_kb_signals(self):
        def _handle_bt_kb_connection(keyboard_mac_address):
            PTLogger.info(
                "BTManager: connection detected for " +
                str(keyboard_mac_address)
            )
            on_bt_connection_detected(
                keyboard_mac_address)

        def _handle_bt_kb_disconnection(keyboard_mac_address):
            PTLogger.info(
                "BTManager: disconnection detected for " +
                str(keyboard_mac_address)
            )
            on_bt_disconnection_detected(
                keyboard_mac_address)

        def _handle_bt_kb_event(changed, path, keyboard_mac_address):
            if path == DeviceHelper.get_device_path(keyboard_mac_address):
                for k, v in changed.items():
                    if k == "Connected":
                        PTLogger.info(
                            "Connection event detected for last connected "
                            "pi-top Bluetooth keyboard"
                        )
                        if v == 1:
                            _handle_bt_kb_connection(keyboard_mac_address)
                        elif v == 0:
                            _handle_bt_kb_disconnection(keyboard_mac_address)
                        break
            else:
                PTLogger.debug(
                    "Bluetooth 'property_changed' event ignored. "
                    "This event is not associated with pi-top Bluetooth keyboard"
                )

        def property_changed(interface, changed, invalidated, path):
            # for name, value in changed.items():
            #     print("{%s.PropertyChanged} [%s] %s = %s" % (interface[interface.rfind(".") + 1:], path, name,
            #                                                  str(value)))
            if interface == DEVICE_INTERFACE:
                if self._keyboard_mac_address != "":
                    try:
                        _handle_bt_kb_event(
                            changed, path, self._keyboard_mac_address)
                    except BluezNoDeviceException:
                        if not self.trying_to_connect:
                            PTLogger.warning(
                                "Error: unable to process property_changed event for expected keyboard: "
                                + str(self._keyboard_mac_address)
                                + " - no Bluez device found; clearing mac address"
                            )
                            self.clear_keyboard_mac_address()
                        else:
                            PTLogger.info(
                                "Warning: unable to process property_changed event for expected keyboard: "
                                + str(self._keyboard_mac_address)
                                + " - no Bluez device found; currently trying to pair - doing nothing"
                            )
                else:
                    PTLogger.debug(
                        "Bluetooth property_changed event ignored. "
                        "This device is not currently associated with a keyboard"
                    )

        self._bt_manager._bus.add_signal_receiver(
            property_changed,
            bus_name="org.bluez",
            dbus_interface="org.freedesktop.DBus.Properties",
            signal_name="PropertiesChanged",
            path_keyword="path",
        )
