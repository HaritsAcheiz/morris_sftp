from httpx import Client
from dataclasses import dataclass
from urllib.parse import urljoin
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class AirtableApi:
    session: Client() = None
    base_api: str = 'https://api.airtable.com'


    def authenticate(self, base_id, table_name, token):
        headers = {
            "Authorization": f"Bearer {token}"
        }
        endpoint = urljoin(self.base_api, f"/v0/{base_id}/{table_name}")
        self.client = Client(headers=headers)
        response = self.client.get(endpoint)
        print(response.text)

if __name__ == '__main__':
    api = AirtableApi()
    api.authenticate(base_id=os.getenv('AIRTABLE_BASE_ID'), table_name=os.getenv('AIRTABLE_TABLE_NAME'), token=os.getenv('AIRTABLE_TOKEN'))
