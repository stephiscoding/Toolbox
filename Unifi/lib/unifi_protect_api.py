import requests

class UnifiProtectAPI:
    def __init__(self, URL, api_key):
        self.URL = URL
        self.headers = {
            "Accept": "application/json",
            "X-API-Key": api_key
        }

    def get_sites(self):
        response = requests.get(
            f"{self.URL}/v1/hosts",
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"API Error: {response.status_code}")
        
    def get_all_cameras(self, console_id):
        response = requests.get(
            f"{self.URL}/v1/connector/consoles/{console_id}/proxy/protect/integration/v1/cameras",
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code}")
        
    def get_camera_details(self, console_id, camera_id):
        response = requests.get(
            f"{self.URL}/v1/connector/consoles/{console_id}/proxy/protect/integration/v1/cameras/{camera_id}",
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code}")
        
    def disable_camera_microphone(self, console_id, camera_id):
        response = requests.post(
            f"{self.URL}/v1/connector/consoles/{console_id}/proxy/protect/integration/v1/cameras/{camera_id}/disable-mic-permanently",
            headers=self.headers
        )
        if response.status_code == 200:
            return
        else:
            print(response.json())
            raise Exception(f"API Error: {response.status_code}")