import pandas as pd
import re
import numpy as np

def to_handle(title):
    if pd.isna(title):
        return None
    title.replace('-', '')
    pattern = re.compile(r"\b[a-zA-Z0-9]+\b")
    matches = pattern.findall(title.lower().strip())
    result = '-'.join(matches)

    return result


def generate_category(*args):
    cat_list = [x for x in list(args[0]) if str(x) != 'nan']
    if len(cat_list) == 0:
        return ''

    return ' > '.join(cat_list)


def to_tags(theme):
    if pd.isna(theme):
        return ''

    return theme.replace(';', ',')


def to_shopify(morris_file_path):
    shopify_df = pd.read_csv('../asset/products_export_10.csv', nrows=0)
    morris_df = pd.read_excel(morris_file_path)
    print(shopify_df)
    print(morris_df.columns)
    shopify_df['Handle'] = morris_df['ProductName'].apply(to_handle)
    shopify_df['Title'] = morris_df['FormattedName']
    shopify_df['Body (HTML)'] = morris_df['FullDescription']
    shopify_df['Vendor'] = morris_df['Brand']
    shopify_df['Product Category'] = morris_df.apply(lambda x: generate_category((x['PrimaryCategory'],
                                                                                  x['SecondaryCategory'],
                                                                                  x['ThirdCategory'])), axis=1)
    shopify_df['Type'] = 'Customes',
    shopify_df['Tags'] = morris_df['Theme'].apply(to_tags),
    shopify_df.loc['Published'] = True,
    shopify_df['Option1 Name'] = morris_df['VariantType1']
    shopify_df['Option1 Value'] = morris_df['VariantValue1']
    shopify_df['Option1 Linked To'] = ''
    shopify_df['Option2 Name'] = morris_df['VariantType2']
    shopify_df['Option2 Value'] = morris_df['VariantValue2']
    shopify_df['Option2 Linked To'] = ''
    shopify_df['Option3 Name'] = morris_df['VariantType3']
    shopify_df['Option3 Value'] = morris_df['VariantValue2']
    shopify_df['Option3 Linked To'] = ''
    shopify_df['Variant SKU'] = morris_df['Sku']
    shopify_df['Variant Grams'] = morris_df['itemWeight']
    shopify_df['Variant Inventory Tracker'] = 'shopify'

    print(shopify_df)


if __name__ == '__main__':
    to_shopify('../data/All_Products_PWHSL.xlsx')
