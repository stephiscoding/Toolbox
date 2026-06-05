from unifi-protect-api import UnifiProtectAPI
import requests
import time

def get_company_from_mac(mac_address):
    response = requests.get(
        f"https://api.maclookup.app/v2/macs/{mac_address}/company/name"
    )
    # the API we're using has a rate limit of 10 requests per second. I could be fancy here, but why bother?
    time.sleep(0.1)
    return response.text

api_key = ""

if __name__ == "__main__":
    api = UnifiProtectAPI("https://api.ui.com", api_key)
    sites = api.get_sites()
    for site in sites:
        print(f"Checking site {site["reportedState"]["name"]}...")
        try:
            cameras = api.get_all_cameras(site["id"])
            for camera in cameras:
                # check that the camera is a Unifi camera - we can only disable mics on first-party cameras.
                is_unifi_camera = get_company_from_mac(camera["mac"]) == "Ubiquiti Inc"
                if camera["isMicEnabled"] != False and is_unifi_camera:
                    print(f"Camera {camera["name"]} has microphone enabled! Disabling...")
                    api.disable_camera_microphone(site["id"], camera["id"])
                else:
                    print(f"Camera {camera["name"]} already has microphone disabled.")
        except Exception:
            print("Error accessing this site. Is the user the owner of this site?")
