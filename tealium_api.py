import requests

API_KEY = "your_api_key"
AUTH_HEADER = {"Authorization": f"Bearer {API_KEY}"}
BASE_URL = "https://api.tealiumiq.com"

def test_telemetry_api():
    endpoint = "/v1/telemetry"
    url = BASE_URL + endpoint
    response = requests.get(url, headers=AUTH_HEADER)
    if response.status_code == 200:
        telemetry_data = response.json()
        return telemetry_data
    else:
        print("Error: Failed to fetch telemetry data.")
        return None

# Example usage
telemetry_data = test_telemetry_api()
if telemetry_data:
    print(telemetry_data)
