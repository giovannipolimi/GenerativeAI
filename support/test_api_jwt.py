import jwt
import requests
import time
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPProxyAuth

# 
for i in ['https_proxy', 'http_proxy', 'proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    if i in os.environ:
        # Remove the variable
        print(f'removing \{i\}')
        del os.environ[i]

# 
vault_path = '/home/g.palazzo/UNIPOL-Digital-Lab/.config/vault'
load_dotenv(vault_path)

# 
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
JWT_URL = 'https://ims-na1.adobelogin.com/ims/exchange/jwt/'

# 
# Define the payload
payload = {
    "exp": int(time.time()) + 3600,
    "iss": "E344E271567ABA6C7F000101@AdobeOrg",
    "sub": "679629EF6437B53C0A495E27@techacct.adobe.com",
    "https://ims-na1.adobelogin.com/s/ent_analytics_bulk_ingest_sdk": True,
    "aud": f"https://ims-na1.adobelogin.com/c/\{CLIENT_ID\}"
}

# 
# Define the private key
with open('/home/g.palazzo/api_config/private.key') as f:
    private_key = f.read()

# 
# Define the headers
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# 
proxy_servers = {
   'http': os.getenv("proxy"),
   'https': os.getenv("https_proxy")
}

proxy_servers

# 
# Make the request to Adobe Login
response = requests.post(
    JWT_URL,
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "jwt_token": jwt.encode(payload, private_key, algorithm="RS256")
    },
    headers=headers,
    proxies=proxy_servers,
    verify=False
)

print(response)

# 
token_path = "/home/g.palazzo/api_config/access_token.json"

# Extract the access token from the response
access_token = response.json()["access_token"]
print(access_token)
print('\n')

with open(token_path, 'w') as f:
    tmp_dump = {
        "token" : access_token,
        "JWT_URL" : JWT_URL,
        "CLIENT_SECRET" : CLIENT_SECRET,
        "CLIENT_ID" : CLIENT_ID
    }

    json.dump(tmp_dump, f)
    print(f"token saved in \{token_path\}")