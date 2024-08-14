import os
from tkinter import *
from tkinter import filedialog
from shopifyapi import ShopifyApp

# Filebrowser function
def browse_file():
    filename = filedialog.askopenfilename(initialdir='./',
        title='Select file to upload',
        filetypes=[('Csv file', '*.csv'), ("All files", "*.*")]
        )

    import_file_entry.insert(END, filename)

def ok_button():
    sa = ShopifyApp(store_name=store_name_entry.get(), access_token=access_token_entry.get())
    client = sa.create_session()
    sa.csv_to_jsonl(csv_filename=import_file_entry.get(), jsonl_filename='bulk_op_vars.jsonl')
    staged_target = sa.generate_staged_target(client)
    sa.upload_jsonl(staged_target=staged_target, jsonl_path="bulk_op_vars.jsonl")
    sa.create_products(client, staged_target=staged_target)


# UI Build
window = Tk()

# Window Config
window.title('Shopify Uploader')
window.geometry('670x280')
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
access_token_entry.grid(column=3, row=0)


# Import File
import_file_label = Label(window, text='Import file: ', bg='light grey')
import_file_label.grid(column=0, row=1, pady=10, sticky='NW')

import_file_entry = Entry(window, width=80)
import_file_entry.grid(column=1, row=1, columnspan=3, sticky='W')

import_file_button = Button(window, text='Browse', command=browse_file, bg='light grey')
import_file_button.grid(column=3, row=1, sticky='E')


# Ok Button
check_img = PhotoImage(file='../asset/vecteezy_check-mark-icon_15130843.png')
ok_button_img = check_img.subsample(400, 400)
ok_button = Button(window,
                   text='Ok',
                   image=ok_button_img,
                   compound='left',
                   bg='light grey',
                   width=41,
                   height=20,
                   command=ok_button)
ok_button.grid(column=3, row=3, sticky='SE', pady=(135, 15))




window.mainloop()
