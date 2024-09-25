from pathlib import Path
import shutil
from sftp import connect_sftp, get_latest_files, download_file, list_directory
import os
from dotenv import load_dotenv
from converter import *
from shopifyapi import ShopifyApp
import time
import asyncio

load_dotenv()

sa = None

def import_status(client):
    # Check Bulk Import status
    print('Checking')
    global sa
    response = sa.pool_operation_status(client)
    if response['data']['currentBulkOperation']['status'] == 'COMPLETED':
        created = True
    else:
        time.sleep(10)
        created = False

    return created

if __name__ == '__main__':
    hostname = os.getenv('MC_HOST')
    username = os.getenv('MC_USER')
    password = os.getenv('MC_PASS')
    remote_path = '/'
    local_path = Path('./data')
    if local_path.exists():
        shutil.rmtree(local_path)
    local_path.mkdir(mode=0o777, parents=True, exist_ok=True)

    sftp = None

    # Download file from SFTP

    try:
        sftp = connect_sftp(hostname, username, password)

    # Get list of file
        # list_directory(sftp, remote_path=remote_path)

    # Get latest file
        latest_full_product, latest_inventory = get_latest_files(sftp, remote_path)
        os.makedirs(local_path, exist_ok=True)
        print(latest_full_product)
        if latest_full_product:
            download_file(sftp, os.path.join(remote_path, latest_full_product),
                          os.path.join(local_path, latest_full_product))
        else:
            print("No AvailableBatch_Full_Product_Data file found")

        # print(latest_inventory)
        # if latest_inventory:
        #     download_file(sftp, os.path.join(remote_path, latest_inventory),
        #                   os.path.join(local_path, latest_inventory))
        # else:
        #     print("No AvailableBatch_Inventory_Only file found")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if sftp:
            sftp.close()

    # hardcode path to test
    full_product_path = f'./data/{latest_full_product}'
    # inventory_path = f'./data/{latest_inventory}'

    # Parse xml file and convert to shopify template
    try:
        full_product_path = os.path.join(local_path, latest_full_product)
        # inventory_path = os.path.join(local_path, latest_inventory)
        convert_to_shopify(file_path=full_product_path, file_type='full')
        # convert_to_shopify(file_path=inventory_path, file_type='inventory')
    except FileNotFoundError as e:
        print(e)

    sa = ShopifyApp(store_name=os.getenv('STORE_NAME'), access_token=os.getenv('ACCESS_TOKEN'))
    client = sa.create_session()

    # ===========================================Get product_id by sku==================================================
    asyncio.run(sa.async_get_id_for_skus())

    # =====================================Bulk update Shopify variant price================================================
    csv_to_jsonl(csv_filename='data/morris_full_inventory_shopify_var_id_inv_id.csv', jsonl_filename='bulk_op_vars.jsonl', mode='vup')
    staged_target = sa.generate_staged_target(client)
    sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
    sa.update_variants(client, staged_target=staged_target)
    created = False
    while not created:
        created = import_status(client)

    # ======================================Update Shopify variant inv qty==========================================
    chunked_quantities = csv_to_quantities(csv_filename='data/morris_full_inventory_shopify_var_id_inv_id.csv', mode='update')
    for quantities in chunked_quantities:
        sa.update_inventories(client, quantities=quantities)
