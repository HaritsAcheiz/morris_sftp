# import all class from tkinter
from os import access
from tkinter import *

# import filedialog method from tkinter
from tkinter import filedialog

# Filebrowser function
def browse_file():
    filename = filedialog.askopenfilename(initialdir='./',
        title='Select file to upload',
        filetypes=[('Csv file', '*.csv'), ("All files","*.*")]
        )

    import_file_entry.insert(END, filename)


# UI Build
window = Tk()

# Window Config
window.title('Shopify Uploader')
window.geometry('700x200')
window.config(bg='light grey', padx=15, pady=15)


# Store name input
store_name_label = Label(window, text='Store Name: ', width=13)
store_name_label.grid(column=0, row=0)

store_name_entry = Entry(window)
store_name_entry.grid(column=1, row=0,)



# access token input
access_token_label = Label(window, text='Access Token: ', width=13)
access_token_label.grid(column=2, row=0)

access_token_entry = Entry(window)
access_token_entry.grid(column=3, row=0)


# Import File
import_file_label = Label(window, text='Import file: ')
import_file_label.grid(column=0, row=1, padx=15)

import_file_entry = Entry(window)
import_file_entry.configure(width=65)
import_file_entry.grid(column=0, row=2, columnspan=3)

import_file_button = Button(window, text='Browse', command=browse_file)
import_file_button.grid(column=3, row=2)


window.mainloop()
