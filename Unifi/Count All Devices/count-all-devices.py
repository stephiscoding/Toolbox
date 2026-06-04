from unifi-network-api import UnifiNetworkAPI

controller_url = ""
username = ""
password = ""

api = UnifiNetworkAPI(controller_url, username, password)

sites = api.get_sites()

number_of_devices = {}

for site in sites:
    devices = api.get_devices(site)
    number_of_devices[sites[site]] = len(devices)

total = 0
for site in number_of_devices:
    print(f"Number of devices at {site}: {number_of_devices[site]}")
    total += number_of_devices[site]
print(f"Total number of devices at all ({len(number_of_devices)}) sites: {total}")