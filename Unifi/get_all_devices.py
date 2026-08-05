import csv
import os
import pprint

from lib.unifi_network_api import UnifiNetworkAPI

controller_url = os.getenv('CONTROLLER_URL')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

api = UnifiNetworkAPI(controller_url, username, password)

sites = api.get_sites()

# data structure:
# {
#   site name:
#       {
#          device mac:
#               {
#                   'friendly_name':
#                   'model':
#                   'serial number':
#                   'in LTS': true/false
#                   'in EOL': true/false
#               }
#       }
# }

devices_info = {}

for site in sites:
    site_friendly_name = sites[site]
    devices_info[site_friendly_name] = {}
    print(f"Getting devices for {site_friendly_name}")
    devices = api.get_devices(site)
    for device in devices:
        device_info = api.get_device_info(site, device['mac'])
        try:
            devices_info[site_friendly_name][device['mac']] = {
                'friendly_name': device_info[0]['name'],
                'model': device_info[0]['model'],
                'serial_number': device_info[0]['serial'],
                'in_LTS': device_info[0]['model_in_lts'],
                'in_EOL': device_info[0]['model_in_eol']
            }
        except KeyError:
            pprint.pprint(device_info, compact=True)
with open('all_unifi_devices.csv', 'w+') as f:
    fieldnames = ['Site', 'Device Name', 'Model', 'Device MAC', 'Device Serial']
    csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
    csv_writer.writeheader()
    for site in devices_info:
        for device in devices_info[site]:
            try:
                csv_writer.writerow({
                    'Site': site,
                    'Device Name': devices_info[site][device]['friendly_name'],
                    'Model': devices_info[site][device]['model'],
                    'Device MAC': device,
                    'Device Serial': devices_info[site][device]['serial_number']
                })
            except KeyError:
                print(devices_info[site][device])
