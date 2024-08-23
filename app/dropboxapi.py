import json
from urllib.parse import urljoin
from httpx import Client
from dataclasses import dataclass
import glob
import os
from dotenv import load_dotenv
from dropbox import Dropbox
import pandas as pd
from dropbox.sharing import SharedLinkSettings, RequestedVisibility

load_dotenv()

def upload_and_get_link():
    dropboxapi = Dropbox(oauth2_access_token=os.getenv('HARITS_DROPBOX_TOKEN'), app_key=os.getenv('HARITS_DROPBOX_APP_KEY'),
                     app_secret=os.getenv('HARITS_DROPBOX_APP_SECRET'))
    os.chdir("../data/images")
    records = list()
    for file in glob.glob("*.jpeg")[0:5]:
        record = dict()
        with open(file, 'rb') as f:
            path = f'/{file}'
            print(f'Uploading...{file}')
            dropboxapi.files_upload(f=f.read(), path=path, autorename=True)
        print(f'Creating link...{file}')
        settings = SharedLinkSettings(requested_visibility=RequestedVisibility.public)
        response = dropboxapi.sharing_create_shared_link_with_settings(path, settings=settings)
        if '(' in response.name:
            record['handle'] = response.name.split('(')[0]
        else:
            record['handle'] = response.name.split('.j')[0]
        record['filename'] = response.name
        record['image_url'] = response.url + '&raw=1'
        records.append(record.copy())
    image_df = pd.DataFrame.from_records(records)
    image_df.to_csv('../product_images.csv', index=False)

    # response = dropboxapi.sharing_list_shared_links()
    # print(response)

    dropboxapi.close()
    return image_df

if __name__ == '__main__':
    upload_and_get_link()

