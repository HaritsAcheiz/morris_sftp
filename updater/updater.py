from json import load
import os
import pandas as pd
from pandas.core.apply import Axis
from shopifyapi import ShopifyApp
from converter import *
import time
from dotenv import load_dotenv

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


def main():
    global sa
    sa = ShopifyApp(store_name=os.getenv('STORE_NAME'), access_token=os.getenv('ACCESS_TOKEN'))
    client = sa.create_session()

    # =====================================Convert morris file into shopify file======================================
    to_shopify(morris_file_path='data/All_Products_PWHSL.xlsx')

    # =========================================Get product_id by handle===============================================
    temp_df = pd.read_csv('data/temp.csv')
    chunked_handles = get_handles(temp_df)
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
    for update_df in chunked_df:

        # =========================================Get product_id by handle===============================================
        handles = update_df['Unique Handle'].to_list()
        product_ids = sa.get_products_id_by_handle(client, handles=handles)['data']['products']['edges']
        extracted_product_ids = [x['node'] for x in product_ids]
        product_id_handle_df = pd.DataFrame.from_records(extracted_product_ids)
        product_id_handle_df.to_csv('data/update_product_ids.csv', index=False)

        # ========================================Fill create product_id =================================================
        fill_product_id(update_df, product_id_filepath='data/update_product_ids.csv', mode='update')

        # ===============================Get variant_id and inventory id by product id=====================================
        update_df['id_number'] = update_df.apply(lambda x: x['id'].split('/')[-1], axis=1)
        product_ids = update_df['id_number']
        f_prod_id = ','.join(product_ids)
        variables = {'query': "product_ids:{}".format(f_prod_id)}
        variant_ids = sa.get_variants_id_by_query(client, variables=variables)['data']['productVariants']['edges']
        extracted_variant_ids = [{'product_id': x['node']['product']['id'], 'variant_id': x['node']['id'], 'inventory_id': x['node']['inventoryItem']['id']} for x in variant_ids]
        variant_id_df = pd.DataFrame.from_records(extracted_variant_ids)
        variant_id_df.to_csv('data/update_product_vids_invids.csv', index=False)

        # ========================================Fill create product_id =================================================
        fill_variant_id(update_df, product_id_filepath='data/update_product_vids_invids.csv', mode='update')

        # =====================================Bulk update Shopify variant price================================================
        csv_to_jsonl(csv_filename='data/update_product_variants_with_vids_invids.csv', jsonl_filename='bulk_op_vars.jsonl', mode='vup')
        staged_target = sa.generate_staged_target(client)
        sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
        sa.bulk_update_variants(client, staged_target=staged_target)
        created = False
        while not created:
            created = import_status(client)

        # =====================================Update Shopify variant inv qty================================================
        quantities = csv_to_quantities(csv_filename='data/update_product_variants_with_vids_invids.csv')
        print(quantities)
        sa.update_inventories(client, quantities=quantities)


if __name__ == '__main__':
    main()
