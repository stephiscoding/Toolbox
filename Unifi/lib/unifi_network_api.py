import requests

class UnifiNetworkAPI:
    def __init__(self, controller_url, username, password):
        self.session = requests.Session()
        self.controller_url = controller_url
        self.login(username, password)

    # log into Unifi Controller.
    def login(self, username, password):
        response = self.session.post(
            f"{self.controller_url}/api/login",
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            return
        else: 
            raise Exception(f"API Error when logging in: {response.status_code}")

    # get a list of all the sites we have access to
    def get_sites(self):
        response = self.session.get(
            f"{self.controller_url}/api/self/sites",
        )

        if response.status_code == 200:
            sites = response.json()["data"]
            site_info = {}
            for site in sites:
                # name is the site id. desc is the friendly name of the site.
                site_info[site["name"]] = site["desc"]
            return site_info
        else:
            raise Exception(f"API Error getting sites list: {response.status_code}")
    
    # get a list of all devices attached to a site
    def get_devices(self, site_id):
        response = self.session.get(
            f"{self.controller_url}/api/s/{site_id}/stat/device-basic"
        )
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"API Error getting device list: {response.status_code}")
        
    # get info on a specific device
    def get_device_info(self, site_id, MAC_address):
        response = self.session.get(
            f"{self.controller_url}/api/s/{site_id}/stat/device/{MAC_address}"
        )
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"API Error when getting device info: {response.status_code}")
        
    # set the tx power of an AP to low    
    def set_device_tx_power(self, site_id, device):
        current_device_info = self.get_device_info(site_id, device["mac"])
        current_device_info[0]["radio_table"][0]["tx_power_mode"] = "low"
        current_device_info[0]["radio_table"][1]["tx_power_mode"] = "low"
        device_id = current_device_info[0].get("_id", device["mac"])
        response = self.session.put(
            f"{self.controller_url}/api/s/{site_id}/rest/device/{device_id}",
            json=current_device_info[0]
        )
        if response.status_code == 200:
            # now that we have set the power level, we have to force the AP to re-provision
            response = self.session.post(
                f"{self.controller_url}/api/s/{site_id}/cmd/devmgr",
                json={
                    "cmd": "force-provision",
                    "mac": device["mac"]
                }
            )
            if response.status_code == 200:
                return
            else:
                raise Exception(f"API Error when provisioning AP: {response.status_code}")
        else:
            raise Exception(f"API Error when setting TX power: {response.status_code}")


if __name__ == "__main__":
    pass