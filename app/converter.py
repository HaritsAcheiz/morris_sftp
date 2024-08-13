import pandas as pd
import re
import numpy as np

def to_handle(title):
    if pd.isna(title):
        return ''
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
    if (theme == '') | pd.isna(theme):
        result = ''
    else:
        result = theme.replace(';', ',')

    return result

def generate_image(image_urls):
    print(image_urls)
    if (len(image_urls) == 0) | (pd.isna(image_urls)):
        result = ''
    else:
        result = ';'.join(image_urls)

    return result

def to_alt_text(image_url):
    if (image_url == '') | (pd.isna(image_url)):
        result = ''
    else:
        result = image_url.split('/')[-1].split('.')[0]
    print(result)

    return result


def to_shopify(morris_file_path):
    morris_df = pd.read_excel(morris_file_path)
    shopify_df = pd.read_csv('./data/products_export_10.csv', nrows=1)
    print(morris_df.columns)
    print(shopify_df.columns)
    print(shopify_df['Variant Requires Shipping'])
    shopify_df = pd.DataFrame()
    shopify_df['Handle'] = morris_df['ProductName'].apply(to_handle)
    shopify_df['Title'] = morris_df['FormattedName']
    shopify_df['Body (HTML)'] = morris_df['FullDescription']
    shopify_df['Vendor'] = morris_df['Brand']
    shopify_df['Product Category'] = morris_df.apply(lambda x: generate_category((x['PrimaryCategory'],
                                                                                  x['SecondaryCategory'],
                                                                                  x['ThirdCategory'])), axis=1)
    shopify_df['Type'] = 'Costumes'
    shopify_df['Tags'] = morris_df['Theme'].apply(to_tags)
    shopify_df['Published'] = True
    shopify_df['Option1 Name'] = morris_df['VariationType1']
    shopify_df['Option1 Value'] = morris_df['VariationValue1']
    shopify_df['Option1 Linked To'] = ''
    shopify_df['Option2 Name'] = morris_df['VariationType2']
    shopify_df['Option2 Value'] = morris_df['VariationValue2']
    shopify_df['Option2 Linked To'] = ''
    shopify_df['Option3 Name'] = ''
    shopify_df['Option3 Value'] = ''
    shopify_df['Option3 Linked To'] = ''
    shopify_df['Variant SKU'] = morris_df['Sku']
    shopify_df['Variant Grams'] = morris_df['ItemWeight']
    shopify_df['Variant Inventory Tracker'] = 'shopify'
    shopify_df['Variant Inventory Qty'] = 0
    shopify_df['Variant Inventory Policy'] = 'deny'
    shopify_df['Variant Inventory Fulfillment Service'] = 'manual'
    shopify_df['Variant Price'] = morris_df['Price']
    shopify_df['Variant Compare At Price'] = ''
    shopify_df['Variant Requires Shipping'] = True
    shopify_df['Variant Taxable'] = True
    shopify_df['Variant Barcode'] = morris_df['Selling Unit Master UPC']
    shopify_df['Image Src'] = morris_df.apply(lambda x: generate_image((x['PrimaryImgLink'],
                                                                        x['ImgAlternate1'],
                                                                        x['ImgAlternate2'],
                                                                        x['ImgAlternate3'],
                                                                        x['ImgAlternate4'],
                                                                        x['ImgAlternate5'],
                                                                        x['ImgAlternate6'])), axis=1)
    shopify_df['Image Position'] = 1
    shopify_df['Image Alt Text'] = morris_df['PrimaryImgLink']


    print(shopify_df)


if __name__ == '__main__':
    to_shopify('./data/All_Products_PWHSL.xlsx')
