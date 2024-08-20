import json
from urllib.parse import urljoin
from httpx import Client
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

class DropboxAPI:
    client: Client() = None
    base_api_url: str = 'https://api.dropboxapi.com'
    base_url: str = 'https://www.dropbox.com'
    access_token: str = None

    def get_authorize(self, app_key, app_secret, auth_code=None):
        endpoint = urljoin(self.base_url, '/oauth2/authorize')
        params = {
            'client_id': app_key,
            # 'client_secret': app_secret,
            # 'token_access_type':'offline',
            'response_type': 'code'
        }
        self.client = Client(follow_redirects=True)
        response = self.client.get(endpoint, params=params)
        response.raise_for_status()
        print(response.content)

    def get_token(self, app_key, app_secret, auth_code=None):
        headers={
            'content-type': 'application/x-www-form-urlencoded'
        }
        endpoint = urljoin(self.base_api_url, '/oauth2/token')
        payload = {
            'code': auth_code,
            'client_id': app_key,
            'grant_type': 'authorization_code',
            'client_secret': app_secret,
        }
        self.client = Client(follow_redirects=True)
        self.client.headers.update(headers)
        response = self.client.post(endpoint, data=payload)
        response.raise_for_status()
        print(response.content)


if __name__ == '__main__':
    dropboxapi = DropboxAPI()
    # dropboxapi.get_authorize(app_key=os.getenv('DROPBOX_APP_KEY'), app_secret=os.getenv('DROPBOX_APP_SECRET'))

    dropboxapi.get_token(app_key=os.getenv('DROPBOX_APP_KEY'),
                         app_secret=os.getenv('DROPBOX_APP_SECRET'),
                         auth_code=os.getenv('DROPBOX_AUTH_CODE'))
