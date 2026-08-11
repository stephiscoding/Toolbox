# every time I update this code, it gets messier and messier. oops.

import os
import time
from datetime import datetime

from lib.unifi_network_api import UnifiNetworkAPI

controller_url = os.getenv("CONTROLLER_URL")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# ng: 2.4Ghz na: 5Ghz nx(?): 6Ghz
radio_table_to_freq = {
    'ng': '2.4Ghz',
    'na': '5Ghz'
}

def get_tx_power(api, site, device):
    device_info = api.get_device_info(site, device["mac"])
    # the radio_table contains information for ALL radios on the APs - this means it contains data for the 2.4GHz band and the 5GHz band, as well as the 6GHz band on supported APs.
    tx_power_modes = {radio_table_to_freq[radio_info['radio']]: radio_info["tx_power_mode"] for radio_info in device_info[0]["radio_table"]}

    # if any of the radios are not broadcasting at low power, returns false.
    return tx_power_modes, all(tx_power_mode == "low" for tx_power_mode in tx_power_modes.values())

def dict_to_table(list_of_dict):
    dict_keys = list_of_dict[0].keys()
    for dictionary in list_of_dict:
        if dictionary.keys() != dict_keys:
            raise Exception("List of dicts is not uniform.")

    output = "<table>"

    # add table headers
    output += f"""
    <thead>
        <th>{"</th><th>".join([key for key in dict_keys])}</th>
    </thead>
    <tbody>
    """

    for dictionary in list_of_dict:
        dict_data = list(dictionary.values())
        output += "<tr><td>"
        output += "</td><td>".join([key for key in dict_data])
        output += "</td></tr>\n"

    output += "</tbody>\n</table>"
    return output

results = []

api = UnifiNetworkAPI(controller_url, username, password)
sites = api.get_sites()
for site in sites:
    print(f"Checking site {sites[site]}...")
    # get basic info for all devices at the site
    devices = api.get_devices(site)
    for device in devices:
        try:
            # if the device is an AP
            if device["type"].lower() == "uap":
                print(f"Checking device {device['name']}...")
                retries = 0
                tx_power_modes_before, tx_is_low = get_tx_power(api, site, device)
                if not tx_is_low:
                    print(
                        f"{device['name']} has some or all radios broadcasting above low power. Fixing..."
                    )
                    # sometimes (e.g. a device is offline), setting the tx power fails, and the API throws a response code that isn't a 200.
                    try:
                        api.set_device_tx_power(site, device)
                        print(
                            "All radios set to low. Waiting 5 seconds, then verifying..."
                        )
                        time.sleep(5)
                    except Exception as e:
                        print("Error setting TX Power:", e)

                    # verify that the setting applied
                    tx_power_modes_after, tx_is_low = get_tx_power(api, site, device)
                    if not tx_is_low:
                        print("Failed to set TX Power to low.")
                    else:
                        print("TX Power successfully set to low.")

                    results.append({
                        'Site': sites[site],
                        'AP Name': device['name'],
                        '2.4Ghz Power Before': tx_power_modes_before['2.4Ghz'],
                        '5Ghz Power Before': tx_power_modes_before['5Ghz'],
                        '6Ghz Power Before': tx_power_modes_before.get('6Ghz', 'n/a'),
                        'Action Taken': '<b>Set Power Levels to Low</b>',
                        '2.4Ghz Power After': tx_power_modes_after['2.4Ghz'],
                        '5Ghz Power After': tx_power_modes_after['5Ghz'],
                        '6Ghz Power After': tx_power_modes_after.get('6Ghz', 'n/a')
                    })
                else:
                    print(
                        f"{device['name']} is already set to low TX power on all radios."
                    )
                    results.append({
                        'Site': sites[site],
                        'AP Name': device['name'],
                        '2.4Ghz Power Before': tx_power_modes_before['2.4Ghz'],
                        '5Ghz Power Before': tx_power_modes_before['5Ghz'],
                        '6Ghz Power Before': tx_power_modes_before.get('6Ghz', 'n/a'),
                        'Action Taken': 'none',
                        '2.4Ghz Power After': tx_power_modes_before['2.4Ghz'],
                        '5Ghz Power After': tx_power_modes_before['5Ghz'],
                        '6Ghz Power After': tx_power_modes_before.get('6Ghz', 'n/a')
                    })
        except:
            print("Error checking/setting power to low. Device is likely offline.")

HTML_table = dict_to_table(results)

user_name = input("What is your name? (for adding to the report): ")

with open('report_template.html', 'r') as f:
    full_html = f.read()

full_html += f"""
<body>
<h1>Unifi AP Power Level Report</h1>
<p><h2>Run by {user_name} at {datetime.strftime(datetime.now(),  '%H:%M on %d/%m/%Y')}</h2></p>
{HTML_table}
</body>
</html>
"""

with open(f"AP Power Levels {datetime.strftime(datetime.now(), '%d-%m-%Y')}.html", "w+") as f:
    f.write(full_html)
