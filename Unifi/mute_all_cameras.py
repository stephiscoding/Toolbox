import json
import os
import time
from datetime import datetime

import requests
from lib.unifi_protect_api import UnifiProtectAPI

api_key = os.getenv("API_KEY")

sites_checked = {}
sites_missed = {}

def get_company_from_mac(mac_address):
    response = requests.get(
        f"https://api.maclookup.app/v2/macs/{mac_address}/company/name"
    )
    # the API we're using has a rate limit of 10 requests per second. I could be fancy here, but why bother?
    time.sleep(0.1)
    return response.text

def check_if_site_is_nvr(site):
    try:
        for controller in site['reportedState']['controllers']:
            if controller['name'] == 'protect':
                return True
    except KeyError:
        return False
    return False

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

if __name__ == "__main__":
    api = UnifiProtectAPI("https://api.ui.com", api_key)
    sites = api.get_sites()
    for site in sites:
        print(f"Checking site {site['reportedState']['name']}...")
        if check_if_site_is_nvr(site):
            try:
                cameras = api.get_all_cameras(site["id"])
                sites_checked[site['reportedState']['name']] = {
                    'before': [],
                    'after': []
                }
                for camera in cameras:
                    # check that the camera is a Unifi camera - we can only disable mics on first-party cameras.
                    is_unifi_camera = get_company_from_mac(camera["mac"]) == "Ubiquiti Inc"
                    if camera["isMicEnabled"] and is_unifi_camera:
                        print(
                            f"Camera {camera['name']} has microphone enabled! Disabling..."
                        )
                        api.disable_camera_microphone(site["id"], camera["id"])
                    else:
                        print(f"Camera {camera['name']} already has microphone disabled.")
                    sites_checked[site['reportedState']['name']]['before'].append({
                        'Camera Name': camera['name'],
                        'Microphone Enabled': 'yes' if camera['isMicEnabled'] and is_unifi_camera else 'no'
                    })
                # get data from the cameras again, and verify that the microphones are disabled
                cameras = api.get_all_cameras(site["id"])
                for camera in cameras:
                    is_unifi_camera = get_company_from_mac(camera["mac"]) == "Ubiquiti Inc"
                    sites_checked[site['reportedState']['name']]['after'].append({
                        'Camera Name': camera['name'],
                        'Microphone Enabled': 'yes' if camera['isMicEnabled'] and is_unifi_camera else 'no'
                    })
            except Exception as e:
                print(e)
                sites_missed[site['reportedState']['name']] = e
        else:
            print(f"{site['reportedState']['name']} is not an NVR.")

user_name = input("What is your name? (for adding to the report): ")

with open('report_template.html', 'r') as f:
    full_html = f.read()

full_html += f"""
<body>
<h1>Unifi Camera Audio Report</h1>
<p><h2>Run by {user_name} at {datetime.strftime(datetime.now(),  '%H:%M on %d/%m/%Y')}</h2></p>
"""

for site in sites_checked:
    full_html += f"<p><h3>Site: {site} before check:</h3></p>"
    full_html += dict_to_table(sites_checked[site]['before'])
    full_html += f"<p><h3>Site: {site} after check:</h3></p>"
    full_html += dict_to_table(sites_checked[site]['after'])
    full_html += "<p><hr /></p>"

full_html += "<p><h3>Was unable to reach the following sites:</h3></p>"
full_html += """
<table>
<thead>
<th>Site</th><th>Error</th>
</thead>
<tbody>
"""
for site in sites_missed:
    full_html += f"<tr><td>{site}</td><td>{sites_missed[site]}</td></tr>"
full_html += "</tbody></table></body>"

with open(f"Unifi Camera Audio Report {datetime.strftime(datetime.now(), '%d-%m-%Y')}.html", "w+") as f:
    f.write(full_html)
