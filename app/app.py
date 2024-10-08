from json import load
import os
from tkinter import *
from tkinter import filedialog
import dropbox
import pandas as pd
from dropboxapi import upload_and_get_link
from shopifyapi import ShopifyApp
from converter import *
import time
from downloader import Downloader


sa = None
staged_target = None
# os.chdir('../')

# Filebrowser function
def browse_file():
    filename = filedialog.askopenfilename(initialdir='',
        title='Select file to upload',
        filetypes=[('Excel files', '*.xlsx'), ('Csv file', '*.csv'), ('All files', '*.*')]
        )

    import_file_entry.insert(END, filename)


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


def import_button():
    # Create Shopify API Session
    global sa
    global staged_target

    sa = ShopifyApp(store_name=store_name_entry.get(), access_token=access_token_entry.get())
    client = sa.create_session()

    # =============================================Get product Id by sku==============================================
    # skus = get_skus()
    # first_skus = ','.join(skus[0:251])
    # first_sku = skus[0]
    # product_ids = sa.get_products_id_by_sku(client, skus=first_sku)

    # =====================================Convert morris file into shopify file======================================
    to_shopify(morris_file_path=import_file_entry.get())
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


    # =============================================Download Image=====================================================
    # download_agent = Downloader()
    # download_agent.create_session()


    # ===============================create products images download==================================================
    # create_df = pd.read_csv('data/create_products.csv')
    # for index in create_df.index:
    #     download_agent.download_image(create_df.iloc[index])
    # download_agent.client.close()


    # ===============================update products images download==================================================
    # update_df = pd.read_csv('data/update_products.csv')
    # for index in update_df.index:
    #     download_agent.download_image(update_df.iloc[index])
    # download_agent.client.close()


    # =======================================Upload Image to Dropbox==================================================
    # upload_and_get_link()

# Product Create
    # ====================================Handle limit with chunked data==============================================
    chunked_df = chunk_data('data/create_products.csv', nrows=249)
    for create_df in chunked_df[0:]:

        # =======================================Merge create product with image =========================================
        image_df = pd.read_csv('data/product_images.csv')
        merge_images(create_df, image_df)

        # =====================================Bulk create Shopify product================================================
        csv_to_jsonl(csv_filename='data/create_products_with_images.csv', jsonl_filename='bulk_op_vars.jsonl', mode='pc')
        staged_target = sa.generate_staged_target(client)
        sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
        sa.create_products(client, staged_target=staged_target)
        created = False
        while not created:
            created = import_status(client)

        time.sleep(300)

        # =========================================Get product_id by handle===============================================
        handles = create_df['Unique Handle'].to_list()
        product_ids = list()
        product_ids = sa.get_products_id_by_handle(client, handles=handles)['data']['products']['edges']
        extracted_product_ids = [{'handle': x['node']['handle'], 'id': x['node']['id']} for x in product_ids]
        product_id_handle_df = pd.DataFrame.from_records(extracted_product_ids)
        product_id_handle_df.to_csv('data/create_product_ids.csv', index=False)

        # ========================================Fill create product_id =================================================
        fill_product_id(create_df, product_id_filepath='data/create_product_ids.csv', mode='create')

        # =====================================Bulk create Shopify variant================================================
        csv_to_jsonl(csv_filename='data/create_products_with_id.csv', jsonl_filename='bulk_op_vars.jsonl', mode='vc')
        staged_target = sa.generate_staged_target(client)
        sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
        sa.create_variants(client, staged_target=staged_target)
        created = False
        while not created:
            created = import_status(client)

        time.sleep(300)

        # =============================================Publish Product================================================
        csv_to_jsonl(csv_filename='data/create_products_with_id.csv', jsonl_filename='bulk_op_vars.jsonl', mode='pp')
        staged_target = sa.generate_staged_target(client)
        sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
        sa.publish_unpublish(client, staged_target=staged_target)
        created = False
        while not created:
            created = import_status(client)

    print(f'Data length : {len(chunked_df)}')


def update_button():
    # Create Shopify API Session
    global sa
    global staged_target

    sa = ShopifyApp(store_name=store_name_entry.get(), access_token=access_token_entry.get())
    client = sa.create_session()

    # =====================================Convert morris file into shopify file======================================
    to_shopify(morris_file_path=import_file_entry.get())

    # =========================================Get product_id by handle===============================================
    chunked_handles = get_handles('data/temp.csv')
    product_ids = list()
    for handles in chunked_handles:
        product_ids.extend(sa.get_products_id_by_handle(client, handles=handles)['data']['products']['edges'])

    extracted_product_ids = [{'handle': x['node']['handle'], 'id': x['node']['id']} for x in product_ids]
    product_id_handle_df = pd.DataFrame.from_records(extracted_product_ids)
    product_id_handle_df.to_csv('data/product_ids.csv', index=False)

    # =======================================Create and Update grouping===============================================
    group_create_update()

# Product Update
    # ====================================Handle limit with chunked data==============================================
    chunked_df = chunk_data('data/update_products.csv', nrows=249)
    for update_df in chunked_df[51:61]:

        # =========================================Get product_id by handle===============================================
        handles = update_df['Unique Handle'].to_list()
        product_ids = list()
        product_ids = sa.get_products_id_by_handle(client, handles=handles)['data']['products']['edges']
        extracted_product_ids = [{'handle': x['node']['handle'], 'id': x['node']['id']} for x in product_ids]
        product_id_handle_df = pd.DataFrame.from_records(extracted_product_ids)
        product_id_handle_df.to_csv('data/update_product_ids.csv', index=False)

        # =======================================Merge create product with image =========================================
        image_df = pd.read_csv('data/product_images.csv')
        merge_images(update_df, image_df, mode='update')

        # ========================================Fill create product_id =================================================
        update_df_with_img = pd.read_csv('data/update_products_with_images.csv')
        fill_product_id(update_df_with_img, product_id_filepath='data/update_product_ids.csv', mode='update')

        # =====================================Bulk update Shopify product================================================
        csv_to_jsonl(csv_filename='data/update_products_with_id.csv', jsonl_filename='bulk_op_vars.jsonl', mode='pu')
        staged_target = sa.generate_staged_target(client)
        sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
        sa.update_products(client, staged_target=staged_target)
        created = False
        while not created:
            created = import_status(client)

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

        # ===================================Bulk Update Shopify variant price============================================
        csv_to_jsonl(csv_filename='data/update_product_variants_with_vids_invids.csv', jsonl_filename='bulk_op_vars.jsonl', mode='vup')
        staged_target = sa.generate_staged_target(client)
        sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
        sa.update_variants(client, staged_target=staged_target)
        created = False
        while not created:
            created = import_status(client)

        # =====================================Update Shopify variant inv qty================================================
        quantities = csv_to_quantities(csv_filename='data/update_product_variants_with_vids_invids.csv')
        sa.update_inventories(client, quantities=quantities)

    print(f'Data length : {len(chunked_df)}')


def close_button():
    pass


# UI Build
window = Tk()

# Window Config
window.title('Shopify Uploader')
# window.geometry('670x280')
window.geometry('930x280')
window.config(bg='light grey', padx=15, pady=15)


# Store name input
store_name_label = Label(window, text='Store Name: ', bg='light grey')
store_name_label.grid(column=0, row=0, pady=10, sticky='NW', padx=(0, 0))

store_name_entry = Entry(window, width=30)
store_name_entry.grid(column=1, row=0)



# access token input
access_token_label = Label(window, text='Access Token: ', bg='light grey')
access_token_label.grid(column=2, row=0, padx=(15, 0))

access_token_entry = Entry(window, width=45)
access_token_entry.grid(column=3, row=0, columnspan=2)


# Import File
import_file_label = Label(window, text='Import file: ', bg='light grey')
import_file_label.grid(column=0, row=1, pady=10, sticky='NW')

import_file_entry = Entry(window, width=80)
import_file_entry.grid(column=1, row=1, columnspan=4, sticky='W')

import_file_button = Button(window, text='Browse', command=browse_file, bg='light grey')
import_file_button.grid(column=4, row=1, sticky='E')


# Logger Text

# Update Button
rocket_img = PhotoImage(file='asset/rocket-svgrepo-com.png')
update_button_img = rocket_img.subsample(10, 10)
update_button = Button(window,
                   text='Update',
                   image=update_button_img,
                   compound='left',
                   bg='light grey',
                   width=70,
                   height=20,
                   command=update_button)
update_button.grid(column=2, row=4, sticky='SE', pady=(135, 15))

# Import Button
rocket_img = PhotoImage(file='asset/rocket-svgrepo-com.png')
import_button_img = rocket_img.subsample(10, 10)
import_button = Button(window,
                   text='Import',
                   image=import_button_img,
                   compound='left',
                   bg='light grey',
                   width=70,
                   height=20,
                   command=import_button)
import_button.grid(column=3, row=4, sticky='SE', pady=(135, 15))

# Close Button
check_img = PhotoImage(file='asset/magnifier-svgrepo-com.png')
check_button_img = check_img.subsample(10, 10)
close_button = Button(window,
                   text='Close',
                   image=check_button_img,
                   compound='left',
                   bg='light grey',
                   width=70,
                   height=20,
                   command=window.destroy)
close_button.grid(column=4, row=4, sticky='SE', pady=(135, 15))




window.mainloop()
