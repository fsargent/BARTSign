#!/usr/bin/env python
import dbus
import uuid
import cv2
import re
import time


# Use the RaspberryPi Camera to look for Wifi QR Codes (Qifi)
# If one is found, change network settings to use it.

cap = cv2.VideoCapture(0)

detector = cv2.QRCodeDetector()

while True:
    _, img = cap.read()
    data, bbox, _ = detector.detectAndDecode(img)

    if(bbox is not None):
        for i in range(len(bbox)):
            cv2.line(img,
                     tuple(bbox[i][0]),
                     tuple(bbox[(i+1) % len(bbox)][0]),
                     color=(255, 0, 255), thickness=2)
        cv2.putText(img,
                    data,
                    (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
        if data:
            print("data found: ", data)
            wifi = QiFiData(data)
            if wifi != False:
                changeWifi(wifi.ssid, wifi.security, wifi.password)
    cv2.imshow("code detector", img)
    if(cv2.waitKey(1) == ord("q")):
        break
cap.release()
cv2.destroyAllWindows()


def QiFiData(data):
    # QiFi codes should be in this format `WIFI:S:<SSID>;T:<WPA|WEP|>;P:<password>;`
    data = "WIFI:T:WEP;S:test;P:rainbows\;unicorns\:jedis\,ninjas\\ secure;;"
    ssid_re = r"(?P<ssid>(?<=S:)((?:[^\;\?\"\$\[\\\]\+])|(?:\\[\\;,:]))+(?<!\\;)(?=;))"
    security_re = r"(?P<security>(?<=T:)[a-zA-Z]+(?=;))"
    password_re = r"(?P<password>(?<=P:)((?:[;,:])|(?:[^;]))+(?<!;)(?=;))"
    try:
        return {
            "ssid": re.search(ssid_re, data).group(),
            "security": re.search(security_re, data).group(),
            "password": re.search(password_re, data).group(),
        }
    except:
        return None


def changeWifi(ssid, security, password):
    # shamelessly stolen from https://stackoverflow.com/questions/15005240/connecting-to-a-protected-wifi-from-python-on-linux/15022137#15022137

    # This script shows how to connect to a WPA protected WiFi network
    # by communicating through D-Bus to NetworkManager 0.9.
    #
    # Reference URLs:
    # http://projects.gnome.org/NetworkManager/developers/
    # http://projects.gnome.org/NetworkManager/developers/settings-spec-08.html
    bus = dbus.SystemBus()
    # Obtain handles to manager objects.
    manager_bus_object = bus.get_object("org.freedesktop.NetworkManager",
                                        "/org/freedesktop/NetworkManager")
    manager = dbus.Interface(manager_bus_object,
                             "org.freedesktop.NetworkManager")
    manager_props = dbus.Interface(manager_bus_object,
                                   "org.freedesktop.DBus.Properties")

    # Enable Wireless. If Wireless is already enabled, this does nothing.
    was_wifi_enabled = manager_props.Get("org.freedesktop.NetworkManager",
                                         "WirelessEnabled")
    if not was_wifi_enabled:
        print("Enabling WiFi and sleeping for 10 seconds ...")
        manager_props.Set("org.freedesktop.NetworkManager", "WirelessEnabled",
                          True)
        # Give the WiFi adapter some time to scan for APs. This is absolutely
        # the wrong way to do it, and the program should listen for
        # AccessPointAdded() signals, but it will do.
        time.sleep(10)

    # Get path to the 'wlan0' device. If you're uncertain whether your WiFi
    # device is wlan0 or something else, you may utilize manager.GetDevices()
    # method to obtain a list of all devices, and then iterate over these
    # devices to check if DeviceType property equals NM_DEVICE_TYPE_WIFI (2).
    device_path = manager.GetDeviceByIpIface("wlan0")
    print("wlan0 path: ", device_path)

    # Connect to the device's Wireless interface and obtain list of access
    # points.
    device = dbus.Interface(bus.get_object("org.freedesktop.NetworkManager",
                                           device_path),
                            "org.freedesktop.NetworkManager.Device.Wireless")
    accesspoints_paths_list = device.GetAccessPoints()

    # Identify our access point. We do this by comparing our desired SSID
    # to the SSID reported by the AP.
    our_ap_path = None
    for ap_path in accesspoints_paths_list:
        ap_props = dbus.Interface(
            bus.get_object("org.freedesktop.NetworkManager", ap_path),
            "org.freedesktop.DBus.Properties")
        ap_ssid = ap_props.Get("org.freedesktop.NetworkManager.AccessPoint",
                               "Ssid")
        # Returned SSID is a list of ASCII values. Let's convert it to a proper
        # string.
        str_ap_ssid = "".join(chr(i) for i in ap_ssid)
        print(ap_path, ": SSID =", str_ap_ssid)
        if str_ap_ssid == ssid:
            our_ap_path = ap_path
            break

    if not our_ap_path:
        print("AP not found :(")
        exit(2)
    print("Our AP: ", our_ap_path)

    # At this point we have all the data we need. Let's prepare our connection
    # parameters so that we can tell the NetworkManager what is the passphrase.
    connection_params = {
        "802-11-wireless": {
            "security": "802-11-wireless-security",
        },
        "802-11-wireless-security": {
            "key-mgmt": "wpa-psk",
            "psk": password
        },
    }

    # Establish the connection.
    settings_path, connection_path = manager.AddAndActivateConnection(
        connection_params, device_path, our_ap_path)
    print("settings_path =", settings_path)
    print("connection_path =", connection_path)

    # Wait until connection is established. This may take a few seconds.
    NM_ACTIVE_CONNECTION_STATE_ACTIVATED = 2
    print("""Waiting for connection to reach """
          """NM_ACTIVE_CONNECTION_STATE_ACTIVATED state ...""")
    connection_props = dbus.Interface(
        bus.get_object("org.freedesktop.NetworkManager", connection_path),
        "org.freedesktop.DBus.Properties")
    state = 0
    while True:
        # Loop forever until desired state is detected.
        #
        # A timeout should be implemented here, otherwise the program will
        # get stuck if connection fails.
        #
        # IF PASSWORD IS BAD, NETWORK MANAGER WILL DISPLAY A QUERY DIALOG!
        # This is something that should be avoided, but I don't know how, yet.
        #
        # Also, if connection is disconnected at this point, the Get()
        # method will raise an org.freedesktop.DBus.Error.UnknownMethod
        # exception. This should also be anticipated.
        state = connection_props.Get(
            "org.freedesktop.NetworkManager.Connection.Active", "State")
        if state == NM_ACTIVE_CONNECTION_STATE_ACTIVATED:
            break
        time.sleep(0.001)
    print("Connection established!")
