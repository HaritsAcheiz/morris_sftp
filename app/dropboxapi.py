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
        dropboxapi.files_upload(f=f.read(), path=f'/{file}', autorename=True)

dropboxapi.close()

