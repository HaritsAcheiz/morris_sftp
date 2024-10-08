import json
from urllib.parse import urljoin
import dropbox
from dropbox import oauth
from dropbox.oauth import OAuth2FlowNoRedirectResult
from httpx import Client
from dataclasses import dataclass
import glob
import os
from dotenv import load_dotenv, set_key
from dropbox import Dropbox, DropboxOAuth2FlowNoRedirect
import pandas as pd
from dropbox.sharing import SharedLinkSettings, RequestedVisibility
import asyncio
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

def upload_and_get_link(dbx):
    records = list()
    file_list = glob.glob("data/images/*.jpeg")
    for file in file_list:
        record = dict()
        with open(file, 'rb') as f:
            path = f"/{file.split('/')[-1]}"
            print(f'Uploading...{file}')
            done = False
            while not done:
                try:
                    dbx.files_upload(f=f.read(), path=path)
                    done = True
                except Exception as e:
                    print(print(e))
                    dbx.check_and_refresh_access_token()
        print(f'Creating link...{file}')
        settings = SharedLinkSettings(requested_visibility=RequestedVisibility.public)
        response = dbx.sharing_create_shared_link_with_settings(path, settings=settings)
        if '(' in response.name:
            record['handle'] = response.name.split('(')[0]
        else:
            record['handle'] = response.name.split('.j')[0]
        record['filename'] = response.name
        record['image_url'] = response.url + '&raw=1'
        records.append(record.copy())
    image_df = pd.DataFrame.from_records(records)
    image_df.to_csv('../product_images.csv', index=False)

    dbx.close()

    return image_df


def get_handle(entry_name):
    filename = entry_name.split('.j')[0]
    if '(' in filename:
        filename = filename.split('(')[0]
    handle = filename

    return handle


def list_files_with_links(dbx, path=''):
    records = list()
    record = dict()
    try:
        # List all files and folders in the given path
        result = dbx.files_list_folder(path, recursive=True)
        # Iterate through each entry
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                try:
                    # Generate a temporary link for the file
                    shared_link = dbx.sharing_list_shared_links(entry.path_display)
                    record['Handle'] = get_handle(entry.name)
                    record['File Name'] = get_handle(entry.name)
                    record['Link'] = shared_link.links[0].url + '&raw=1'
                    print(f"Handle: {get_handle(entry.name)}")
                    print(f"File: {entry.name}")
                    print(f"Shared Link: {shared_link.links[0].url + '&raw=1'}")
                    print("---")
                    records.append(record)
                except Exception as e:
                    print(f"Error getting link for {entry.path_display}: {e}")

        # If there are more entries, continue listing
        while result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    try:
                        shared_link = dbx.sharing_list_shared_links(entry.path_display)
                        record['Handle'] = get_handle(entry.name)
                        record['File Name'] = get_handle(entry.name)
                        record['Link'] = shared_link.links[0].url + '&raw=1'
                        print(f"Handle: {get_handle(entry.name)}")
                        print(f"File: {entry.name}")
                        print(f"Shared Link: {shared_link.links[0].url + '&raw=1'}")
                        print("---")
                        records.append(record)
                    except Exception as e:
                        print(f"Error getting link for {entry.path_display}: {e}")

        images_df = pd.DataFrame.from_records(records)
        images_df.to_csv('data/product_images.csv', index=False)

    except Exception as e:
        print(f"Error listing files: {e}")


def get_shared_link_a(dbx, entry):
    try:
        shared_link = dbx.sharing_list_shared_links(entry.path_display)
        print(f"Handle: {get_handle(entry.name)}")
        print(f"File: {entry.name}")
        print(f"Shared Link: {shared_link.links[0].url + '&raw=1'}")
        return {
            'Handle': get_handle(entry.name),
            'File Name': entry.name,
            'Link': shared_link.links[0].url + '&raw=1'
        }
    except Exception as e:
        print(f"Error getting link for {entry.path_display}: {e}")
        return None

def get_shared_link_from_list(dbx, filepath):
    try:
        shared_link = dbx.sharing_list_shared_links(filepath)
        print(f"Handle: {get_handle(filepath[1:])}")
        print(f"File: {filepath[1:]}")
        print(f"Shared Link: {shared_link.links[0].url + '&raw=1'}")
        return {
            'Handle': get_handle(filepath[1:]),
            'File Name': filepath[1:],
            'Link': shared_link.links[0].url + '&raw=1'
        }
    except Exception as e:
        print(f"Error getting link for {filepath[1:]}: {e}")
        return {
            'Handle': get_handle(filepath[1:]),
            'File Name': filepath[1:],
            'Link': ''
        }


async def list_files_with_links_a(dbx, path=''):
    records = []
    try:
        result = dbx.files_list_folder(path, recursive=True)

        async def process_entries(entries):
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                tasks = [loop.run_in_executor(pool, get_shared_link_a, dbx, entry)
                         for entry in entries if isinstance(entry, dropbox.files.FileMetadata)]
                results = await asyncio.gather(*tasks)
                return [r for r in results if r is not None]

        records.extend(await process_entries(result.entries))

        while result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
            records.extend(await process_entries(result.entries))

        images_df = pd.DataFrame(records)
        images_df.to_csv('data/product_images.csv', index=False)

        # for record in records:
        #     print(f"Handle: {record['Handle']}")
        #     print(f"File: {record['File Name']}")
        #     print(f"Shared Link: {record['Link']}")
        #     print("---")

    except Exception as e:
        print(f"Error listing files: {e}")


async def get_image_url(dbx):
    await list_files_with_links_a(dbx)


def get_dropbox_tokens():
    auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET, token_access_type='offline')

    try:
        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print("2. Click 'Allow' (you might have to log in first)")
        print("3. Copy the authorization code")

        auth_code = input("Enter the authorization code here: ").strip()

        try:
            oauth_result = auth_flow.finish(auth_code)
            print(oauth_result)
            return oauth_result.access_token, oauth_result.refresh_token
        except Exception as e:
            print(f'Error finishing the OAuth flow: {e}')
            return None, None
    except Exception as e:
        print(f'Error starting the OAuth flow: {e}')
        return None, None

def update_env_file(access_token, refresh_token):
    env_path = '../.env'
    set_key(env_path, "DROPBOX_ACCESS_TOKEN", access_token)
    set_key(env_path, "DROPBOX_REFRESH_TOKEN", refresh_token)
    print("Tokens updated in .env file")


if __name__ == "__main__":

    # file_list = glob.glob("data/images/*.jpeg")
    # print(file_list.index('data/images/rod-wig(13).jpeg'))
    dbx = Dropbox(oauth2_access_token=os.getenv('DROPBOX_ACCESS_TOKEN'), app_key=os.getenv('DROPBOX_APP_KEY'),
                  app_secret=os.getenv('DROPBOX_APP_SECRET'), oauth2_refresh_token=os.getenv('DROPBOX_REFRESH_TOKEN'))

    # asyncio.run(get_image_url(dbx))

    with open('data/error_get_links.txt', 'r') as file:
        datas = file.readlines()
    file_paths = [f"/{data.split(':')[0]}" for data in datas]
    url_records = [get_shared_link_from_list(dbx, filepath=filepath) for filepath in file_paths]
    additional_image_urls = pd.DataFrame.from_records(url_records)
    additional_image_urls.to_csv('data/product_images_add.csv')



    # upload_and_get_link(dbx)

    # list_files_with_links(dbx)
    # settings = SharedLinkSettings(requested_visibility=RequestedVisibility.public)
    # dbx.sharing_create_shared_link_with_settings('/demon-seed-latex-mask.jpeg', settings=settings)
    # response = dbx.sharing_list_shared_links('/demon-seed-latex-mask.jpeg', direct_only=True)
    # response = dbx.files_get_metadata('/demon-seed-latex-mask.jpeg')
    # print(response)
    # get_link()
    # access_token, refresh_token = get_dropbox_tokens()
    # if access_token and refresh_token:
    #     print("Access Token:", access_token)
    #     print("Refresh Token:", refresh_token)

    #     # Update .env file
    #     update_env_file(access_token, refresh_token)

    #     # You can now use this access token to initialize a Dropbox object
    #     dbx = dropbox.Dropbox(access_token)
    #     # Test the connection
    #     print(dbx.users_get_current_account())
    # else:
    #     print("Failed to get tokens")

