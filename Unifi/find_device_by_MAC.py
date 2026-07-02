from lib.unifi_network_api import UnifiNetworkAPI
import sys
import pprint

controller_url = ""
username = ""
password = ""

try:
    mac_to_find = sys.argv[1]
except:
    print("Missing argument: please provide the MAC address of the device you're looking for in the format xx:xx:xx:xx:xx:xx.")

try:
    verbosity = sys.argv[2]
except:
    verbosity = "v"

api = UnifiNetworkAPI(controller_url, username, password)
sites = api.get_sites()
for site in sites:
    # get basic info for all devices at the site
    devices = api.get_devices(site)
    for device in devices:
        if device["mac"] == mac_to_find:
            print(f"Found {device["name"]} at site {sites[site]}!")
            if verbosity == "vv":
                device_info = api.get_device_info(site, device["mac"])
                print("Detailed device info:")
                pprint.pprint(device_info, compact=True)
            exit(0)
print("Device not found.")