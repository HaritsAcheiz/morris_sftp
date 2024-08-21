from json import load
import os
from tkinter import *
from tkinter import filedialog
import pandas as pd
from shopifyapi import ShopifyApp
from converter import to_shopify, csv_to_jsonl, group_create_update, get_skus, get_handles
import time


sa = None
staged_target = None

# Filebrowser function
def browse_file():
    filename = filedialog.askopenfilename(initialdir='../',
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
        time.sleep(60)
        created = False

    return created


def import_button():
    # Create Shopify API Session
    global sa
    global staged_target

    sa = ShopifyApp(store_name=store_name_entry.get(), access_token=access_token_entry.get())
    client = sa.create_session()

    # Get product Id by sku
    # skus = get_skus()
    # first_skus = ','.join(skus[0:251])
    # first_sku = skus[0]
    # product_ids = sa.get_products_id_by_sku(client, skus=first_sku)

    # Convert morris file into shopify file
    to_shopify(morris_file_path=import_file_entry.get())
    # fill_product_id()

    # Get product_id by handle
    chunked_handles = get_handles()
    product_ids = list()
    for handles in chunked_handles:
        product_ids.extend(sa.get_products_id_by_handle(client, handles=handles)['data']['products']['edges'])

    extracted_product_ids = [x['node'] for x in product_ids]
    product_id_handle_df = pd.DataFrame.from_records(extracted_product_ids)
    product_id_handle_df.to_csv('../data/product_ids.csv', index=False)

    # Create and Update grouping
    group_create_update()

    # Bulk create Shopify product
    csv_to_jsonl(csv_filename='../data/create_products.csv', jsonl_filename='bulk_op_vars.jsonl')
    staged_target = sa.generate_staged_target(client)
    sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
    sa.create_products(client, staged_target=staged_target)
    created = False
    while not created:
        created = import_status(client)

    # Bulk update Shopify product
    # csv_to_jsonl(csv_filename='../data/update_products.csv', jsonl_filename='bulk_op_vars.jsonl')
    # staged_target = sa.generate_staged_target(client)
    # sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
    # sa.update_products(client, staged_target=staged_target)
    # updated = False
    # while not updated:
    #     updated = import_status(client)

    # Add price



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



# Close Button
check_img = PhotoImage(file='../asset/magnifier-svgrepo-com.png')
check_button_img = check_img.subsample(10, 10)
close_button = Button(window,
                   text='Close',
                   image=check_button_img,
                   compound='left',
                   bg='light grey',
                   width=70,
                   height=20,
                   command=close_button)
close_button.grid(column=3, row=4, sticky='SE', pady=(135, 15))


# Import Button
rocket_img = PhotoImage(file='../asset/rocket-svgrepo-com.png')
import_button_img = rocket_img.subsample(10, 10)
import_button = Button(window,
                   text='Import',
                   image=import_button_img,
                   compound='left',
                   bg='light grey',
                   width=70,
                   height=20,
                   command=import_button)
import_button.grid(column=4, row=4, sticky='SE', pady=(135, 15))


window.mainloop()
