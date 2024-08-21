import json
from urllib.parse import urljoin
from httpx import Client
from dataclasses import dataclass
import glob
import os
from dotenv import load_dotenv
from dropbox import Dropbox

load_dotenv()

dropboxapi = Dropbox(oauth2_access_token=os.getenv('DROPBOX_ACCESS_TOKEN'), app_key=os.getenv('DROPBOX_APP_KEY'),
                     app_secret=os.getenv('DROPBOX_APP_SECRET'))

os.chdir("./data/images")
for file in glob.glob("*.jpeg"):
    with open(file, 'rb') as f:
        path = f'/{file}'
        print(f'Uploading...{file}')
        response = dropboxapi.files_upload(f=f.read(), path=path, autorename=True)
        print(response)
        print(f'Creating link...{file}')
        response = dropboxapi.sharing_create_shared_link_with_settings(path)
        print(response)
response = dropboxapi.sharing_list_shared_links()
print(response)

dropboxapi.close()

