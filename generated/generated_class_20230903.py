import jwt
import requests
import time
import json
import os
from dotenv import load_dotenv
from requests.auth import HTTPProxyAuth

class AdobeLogin:
    def __init__(self):
        # Remove proxy environment variables
        for i in ['https_proxy', 'http_proxy', 'proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
            if i in os.environ:
                print(f'removing {i}')
                del os.environ[i]
        
        # Load environment variables from vault
        vault_path = '/home/g.palazzo/UNIPOL-Digital-Lab/.config/vault'
        load_dotenv(vault_path)
        
        # Get client ID and client secret from environment variables
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        
        # Define JWT URL
        self.JWT_URL = 'https://ims-na1.adobelogin.com/ims/exchange/jwt/'
        
        # Define payload
        self.payload = {
            "exp": int(time.time()) + 3600,
            "iss": "E344E271567ABA6C7F000101@AdobeOrg",
            "sub": "679629EF6437B53C0A495E27@techacct.adobe.com",
            "https://ims-na1.adobelogin.com/s/ent_analytics_bulk_ingest_sdk": True,
            "aud": f"https://ims-na1.adobelogin.com/c/{self.CLIENT_ID}"
        }
        
        # Read private key
        with open('/home/g.palazzo/api_config/private.key') as f:
            self.private_key = f.read()
        
        # Define headers
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Define proxy servers
        self.proxy_servers = {
            'http': os.getenv("proxy"),
            'https': os.getenv("https_proxy")
        }
        
        # Make the request to Adobe Login
        self.response = requests.post(
            self.JWT_URL,
            data={
                "client_id": self.CLIENT_ID,
                "client_secret": self.CLIENT_SECRET,
                "jwt_token": jwt.encode(self.payload, self.private_key, algorithm="RS256")
            },
            headers=self.headers,
            proxies=self.proxy_servers,
            verify=False
        )
        
        # Define token path
        self.token_path = "/home/g.palazzo/api_config/access_token.json"
        
        # Extract the access token from the response
        self.access_token = self.response.json()["access_token"]
        
        # Save token to file
        with open(self.token_path, 'w') as f:
            tmp_dump = {
                "token" : self.access_token,
                "JWT_URL" : self.JWT_URL,
                "CLIENT_SECRET" : self.CLIENT_SECRET,
                "CLIENT_ID" : self.CLIENT_ID
            }
            json.dump(tmp_dump, f)
            print(f"token saved in {self.token_path}")

# Create an instance of the AdobeLogin class
adobe_login = AdobeLogin()