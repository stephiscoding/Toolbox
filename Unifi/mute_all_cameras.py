import os
import time
import json

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

if __name__ == "__main__":
    api = UnifiProtectAPI("https://api.ui.com", api_key)
    sites = api.get_sites()
    for site in sites:
        print(f"Checking site {site['reportedState']['name']}...")
        if check_if_site_is_nvr(site):
            try:
                cameras = api.get_all_cameras(site["id"])
                sites_checked[site['reportedState']['name']] = 0
                for camera in cameras:
                    # check that the camera is a Unifi camera - we can only disable mics on first-party cameras.
                    is_unifi_camera = get_company_from_mac(camera["mac"]) == "Ubiquiti Inc"
                    if camera["isMicEnabled"] and is_unifi_camera:
                        print(
                            f"Camera {camera['name']} has microphone enabled! Disabling..."
                        )
                        api.disable_camera_microphone(site["id"], camera["id"])
                        sites_checked[site['reportedState']['name']] += 1
                    else:
                        print(f"Camera {camera['name']} already has microphone disabled.")
            except Exception as e:
                print(e)
                sites_missed[site['reportedState']['name']] = e
        else:
            print(f"{site['reportedState']['name']} is not an NVR.")
print("\n\nResult:")
print("\n".join([f"Muted {sites_checked[site]} cameras at {site}" for site in sites_checked]))
print("\n".join([f"Couldn't access {site}. Reported error: {sites_missed[site]}" for site in sites_missed]))
