from lib.unifi_network_api import UnifiNetworkAPI
import time

controller_url = ""
username = ""
password = ""

def check_tx_power(api, site, device):
    device_info = api.get_device_info(site, device["mac"])
    # the radio_table contains information for ALL radios on the APs - this means it contains data for the 2.4GHz band and the 5GHz band, as well as the 6GHz band on supported APs.
    # list comprehension because it saves a while TWO (2) lines!!!!
    tx_power_modes = [radio_info["tx_power_mode"] for radio_info in device_info[0]["radio_table"]]
    # if any of the radios are not broadcasting at low power, returns false.
    return all(
        tx_power == "low"
        for tx_power in tx_power_modes
    )

api = UnifiNetworkAPI(controller_url, username, password)
sites = api.get_sites()
for site in sites:
    print(f"Checking site {sites[site]}...")
    # get basic info for all devices at the site
    devices = api.get_devices(site)
    for device in devices:
        # if the device is an AP
        if device["type"].lower() == "uap":
            print(f"Checking device {device["name"]}...")
            retries = 0
            tx_is_low = check_tx_power(api, site, device)
            if not tx_is_low:
                # it should really only take one attempt to set the broadcast power. But it can't hurt to verify and retry if that attempt doesn't work!
                while (not tx_is_low) and retries <= 2:
                    print(f"{device["name"]} has some or all radios broadcasting above low power. Fixing...")
                    # sometimes (e.g. a device is offline), setting the tx power fails, and the API throws a response code that isn't a 200.
                    try:
                        api.set_device_tx_power(site, device)
                        print("All radios set to low. Waiting 5 seconds, then verifying...")
                        time.sleep(5)
                    except Exception as e:
                        print("Error setting TX Power:", e)
                    tx_is_low = check_tx_power(api, site, device)
                    if not tx_is_low:
                        print("TX Power not updated. Retrying...")
                        retries += 1
                    else:
                        print("TX Power successfully set to low.")
                if retries >= 2:
                    print(f"ERROR: Failed to set TX power on {device["name"]}.")
            else:
                print(f"{device["name"]} is already set to low TX power on all radios.")
            