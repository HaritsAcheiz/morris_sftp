from json import load
import os
import pandas as pd
from shopifyapi import ShopifyApp
from converter import *
import time
from dotenv import load_dotenv

load_dotenv()

def main():
    sa = ShopifyApp(store_name=os.getenv('STORE_NAME'), access_token=os.getenv('ACCESS_TOKEN'))
    client = sa.create_session()

    # =============================================Get product Id by sku==============================================
    # skus = get_skus()
    # first_skus = ','.join(skus[0:251])
    # first_sku = skus[0]
    # product_ids = sa.get_products_id_by_sku(client, skus=first_sku)

    # =====================================Convert morris file into shopify file======================================
    to_shopify(morris_file_path='data/All_Products_PWHSL.xlsx')
    # fill_product_id()

    # =========================================Get product_id by handle===============================================
    chunked_handles = get_handles('data/temp.csv')
    product_ids = list()
    for handles in chunked_handles:
        product_ids.extend(sa.get_products_id_by_handle(client, handles=handles)['data']['products']['edges'])

    extracted_product_ids = [x['node'] for x in product_ids]
    product_id_handle_df = pd.DataFrame.from_records(extracted_product_ids)
    product_id_handle_df.to_csv('data/product_ids.csv', index=False)

    # =======================================Create and Update grouping===============================================
    group_create_update()

# Product Update
    # ====================================Handle limit with chunked data==============================================
    chunked_df = chunk_data('data/update_products.csv', nrows=249)
    for update_df in chunked_df[0:1]:
        # =========================================Get product_id by handle===============================================
        chunked_handles = get_handles('data/update_products.csv')
        product_ids = list()
        for handles in chunked_handles:
            product_ids.extend(sa.get_products_id_by_handle(client, handles=handles)['data']['products']['edges'])

        extracted_product_ids = [x['node'] for x in product_ids]
        product_id_handle_df = pd.DataFrame.from_records(extracted_product_ids)
        product_id_handle_df.to_csv('data/update_product_ids.csv', index=False)

        # ========================================Fill create product_id =================================================
        fill_product_id('data/update_products.csv', product_id_filepath='data/update_product_ids.csv', mode='update')

        # =====================================Bulk create Shopify variant================================================
        csv_to_jsonl(csv_filename='data/update_products_with_id.csv', jsonl_filename='bulk_op_vars.jsonl', mode='vu')
        staged_target = sa.generate_staged_target(client)
        sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
        sa.update_variants(client, staged_target=staged_target)
        created = False
        while not created:
            created = import_status(client)

if __name__ == '__main__':
    main()
