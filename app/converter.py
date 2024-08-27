from itertools import product
import pandas as pd
import re
import numpy as np
import json
from urllib.parse import quote, unquote
from ast import literal_eval

weight_unit_mapper = {'lb': 'POUNDS', 'kg': 'KILOGRAMS', 'g': 'GRAMS', 'oz': 'OUNCES'}
tracker_mapper = {'shopify': True, '': False}

def to_handle(title, alt_title):
    if (pd.isna(title)) | (title == 0):
        if pd.isna(alt_title):
            result = None
        else:
            alt_title.replace('-', '')
            pattern = re.compile(r"\b[a-zA-Z0-9]+\b")
            matches = pattern.findall(alt_title.lower().strip())
            result = '-'.join(matches)
    else:
        title.replace('-', '')
        pattern = re.compile(r"\b[a-zA-Z0-9]+\b")
        matches = pattern.findall(title.lower().strip())
        result = '-'.join(matches)

    return result


def get_title(title, alt_title):
    if (pd.isna(title)) | (title == 0):
        if pd.isna(alt_title):
            result = None
        else:
            result = alt_title
    else:
        result = title

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


def generate_image(*args):
    image_urls = [quote(x, safe=':/?&=') for x in list(args[0]) if str(x) != 'nan']
    if len(image_urls) == 0:

        return ''

    else:

        return image_urls


def generate_alt_text(*args):
    image_alt_text = [unquote(x).split('/')[-1].split('.')[0].strip() for x in args[0]]
    if len(image_alt_text) == 0:

        return ''

    else:

        return image_alt_text


def to_shopify(morris_file_path):
    morris_df = pd.read_excel(morris_file_path)
    shopify_df = pd.DataFrame()
    shopify_df['Handle'] = morris_df.apply(lambda x: to_handle(x['ProductName'], alt_title=x['FormattedName']), axis=1)
    shopify_df['Title'] = morris_df.apply(lambda x: get_title(x['FormattedName'], alt_title=x['ProductName']), axis=1)
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
    shopify_df['Variant Inventory Qty'] = morris_df['QOH']
    shopify_df['Variant Inventory Policy'] = 'deny'
    shopify_df['Variant Inventory Fulfillment Service'] = 'manual'
    shopify_df['Variant Price'] = morris_df['MapPrice']
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
    shopify_df['Image Alt Text'] = shopify_df['Image Src'].apply(generate_alt_text)
    shopify_df['Gift Card'] = ''
    shopify_df['SEO Title'] = ''
    shopify_df['SEO Description'] = ''
    shopify_df['Google Shopping / Google Product Category'] = shopify_df['Product Category']
    shopify_df['Google Shopping / Gender'] = morris_df['Gender']
    shopify_df['Google Shopping / Age Group'] = morris_df['Age Group']
    shopify_df['Google Shopping / MPN'] = shopify_df['Variant Barcode']
    shopify_df['Google Shopping / Condition'] = 'New'
    shopify_df['Google Shopping / Custom Product'] = ''
    shopify_df['Google Shopping / Custom Label 0'] = ''
    shopify_df['Google Shopping / Custom Label 1'] = ''
    shopify_df['Google Shopping / Custom Label 2'] = ''
    shopify_df['Google Shopping / Custom Label 3'] = ''
    shopify_df['Google Shopping / Custom Label 4'] = ''
    shopify_df['enable_best_price (product.metafields.custom.enable_best_price)'] = True
    shopify_df['Product rating count (product.metafields.reviews.rating_count)'] = ''
    shopify_df['Variant Image'] = morris_df['PrimaryImgLink']
    shopify_df['Variant Weight Unit'] = 'lb'
    shopify_df['Variant Tax Code'] = ''
    shopify_df['Cost per item'] = morris_df['Price']
    shopify_df['Included / United States'] = ''
    shopify_df['Price / United States'] = ''
    shopify_df['Compare At Price / United States'] = ''
    shopify_df['Included / International'] = ''
    shopify_df['Price / International'] = ''
    shopify_df['Compare At Price / International'] = ''
    shopify_df['Status'] = 'draft'
    shopify_df.dropna(axis=0, subset='Handle', inplace=True, ignore_index=True)
    shopify_df.fillna('', inplace=True)

    shopify_df.to_csv('data/temp.csv', index=False)


def fill_opt(opt_name=None, opt_value=None):
    if opt_name != '':
        opt_attr = {'name': opt_name, 'values': {'name': opt_value}}

        return opt_attr


def fill_media(original_src, alt):
    if original_src != '':
        media_attr = {
            'originalSource': original_src,
            'mediaContentType': 'IMAGE',
            'alt': alt
        }

        return media_attr


def str_to_bool(s):
    if s == 'True':

         return True

    elif s == 'False':

         return False

    else:
         raise ValueError


def get_skus():
    shopify_df = pd.read_csv('data/temp.csv')

    return list(shopify_df['Variant SKU'])


def get_handles(filepath):
    shopify_df = pd.read_csv(filepath)
    handles = list(shopify_df['Handle'])
    n = 250
    chunked_handles = [handles[i:i + n] for i in range(0, len(handles), n)]

    return chunked_handles


def group_create_update():
    # Fill product id
    shopify_df = pd.read_csv('data/temp.csv')
    product_ids_df = pd.read_csv('data/product_ids.csv')
    shopify_df = pd.merge(shopify_df, product_ids_df, how='left', left_on='Handle', right_on='handle')
    shopify_df.fillna('', inplace=True)

    # group update create
    create_df = shopify_df[shopify_df['id'] == '']
    update_df = shopify_df[shopify_df['id'] != '']
    create_df.to_csv('data/create_products.csv')
    update_df.to_csv('data/update_products.csv')

def fill_product_id(product_filepath, product_id_filepath):
    # Fill product id
    shopify_df = pd.read_csv(product_filepath)
    product_ids_df = pd.read_csv(product_id_filepath)
    shopify_df = pd.merge(shopify_df, product_ids_df, how='left', left_on='Handle', right_on='handle')
    shopify_df.fillna('', inplace=True)
    shopify_df.drop(columns=['handle_x', 'id_x', 'handle_y'], inplace=True)
    shopify_df.rename({'id_y': 'id'}, axis=1, inplace=True)
    shopify_df.to_csv('data/create_products_with_id.csv', index=False)


def csv_to_jsonl(csv_filename, jsonl_filename, mode='pc'):
    print("Converting csv to jsonl file...")
    df = pd.read_csv(csv_filename, nrows=5)
    df.fillna('', inplace=True)
    datas = None
    opts = ['Option1 Name', 'Option2 Name', 'Option3 Name']
    if mode == 'vc':
        # Create formatted dictionary
        datas = []
        for index in df.index:
            data_dict = {"productId": str, "variants": list()}
            data_dict['productId'] = df.iloc[index]['id']
            variants = list()
            metafields = list()
            variant = dict()
            variant['Barcode'] = df.iloc[index]['Variant Barcode']
            variant['CompareAtPrice'] = df.iloc[index]['Variant Compare At Price']
            # variant['id'] = df.iloc[index]['id']

            variant_inv_item = dict()
            variant_inv_item['cost'] = df.iloc[index]['Cost per item']
            # variant_inv_item['countryCodeOfOrigin'] = df.iloc[index]['Variant Barcode']
            # variant_inv_item['countryHarmonizedSystemCodes'] = df.iloc[index]['Variant Barcode']
            # variant_inv_item['harmonizedSystemCode'] = df.iloc[index]['Variant Barcode']

            variant_measure = {'weight': {'unit':'', 'value':None}}
            variant_measure['weight']['unit'] = weight_unit_mapper[df.iloc[index]['Variant Weight Unit']]
            variant_measure['weight']['value'] = df.iloc[index]['Variant Grams']

            variant_inv_item['measurement'] = variant_measure
            # variant_inv_item['provinceCodeOfOrigin'] = df.iloc[index]['Variant Barcode']
            variant_inv_item['requiresShipping'] = df.iloc[index]['Variant Requires Shipping']
            variant_inv_item['sku'] = df.iloc[index]['Variant SKU']
            variant_inv_item['tracked'] = tracker_mapper[df.iloc[index]['Variant Inventory Tracker']]
            variant['inventoryItem'] = variant_inv_item
            variant['inventoryPolicy'] = df.iloc[index]['Variant Inventory Policy']

            variant_inv_qty = {'availableQuantity': {'availableQuantity': None, 'locationId':None}}
            variant_inv_qty['availableQuantity'] = df.iloc[index]['Variant Inventory Qty']
            # variant_inv_qty['locationId'] = df.iloc[index]['Variant Barcode']
            variant['inventoryQuantities'] = variant_inv_qty
            # variant['mediaId'] = df.iloc[index]['Variant Barcode']
            # variant['mediaSrc'] = df.iloc[index]['Variant Barcode']

            # metafield = dict()
            # metafield['id'] = df.iloc[index]['Variant Barcode']
            # metafield['key'] = 'custom'
            # metafield['namespace'] = 'enable_best_price'
            # metafield['type'] = 'boolean'
            # metafield['value'] = str(df.iloc[index]['enable_best_price (product.metafields.custom.enable_best_price)'])
            # metafields.append(metafield)

            # variant['metafields'] = metafields

            # opt_value = dict()
            # opt_values = list()
            # opt_value['id'] = df.iloc[index]['Variant Barcode']
            # opt_value['name'] = df.iloc[index]['Opt']
            # opt_value['optionId'] = 'enable_best_price'
            # opt_value['optionName'] = 'boolean'
            # opt_value['value'] = True
            # opt_values.append(opt_value)

            # variant['optionValues'] = opt_values

            variant['price'] = df.iloc[index]['Variant Price']
            # variant['taxCode'] = df.iloc[index]['Variant Barcode']
            variant['taxable'] = df.iloc[index]['Variant Taxable']

            data_dict['variants'] = variants
            datas.append(data_dict.copy())

    elif mode == 'pc':
        # Create formatted dictionary
        datas = []
        for index in df.index:
            data_dict = {"input": dict(), "media": list()}
            # data_dict['input']['category'] = ''
            data_dict['input']['claimOwnership'] = {'bundles': str_to_bool('False')}
            # data_dict['input']['collectionToJoin'] = ''
            # data_dict['input']['collectionToLeave'] = ''
            # data_dict['input']['combinedListingRole'] = 'PARENT'
            data_dict['input']['customProductType'] = df.iloc[index]['Type']
            data_dict['input']['descriptionHtml'] = df.iloc[index]['Body (HTML)']
            data_dict['input']['giftCard'] = str_to_bool('False') #df.iloc[index]['Gift Card']
            # data_dict['input']['giftCardTemplateSuffix'] = ''
            data_dict['input']['handle'] = df.iloc[index]['Handle']
            # data_dict['input']['id'] = ''
            data_dict['input']['metafields'] = {#'id': '',
                                                'key': 'enable_best_price',
                                                'namespace': 'custom',
                                                'type': 'boolean',
                                                'value': str(df.iloc[index]['enable_best_price (product.metafields.custom.enable_best_price)'])
                                                }
            product_options = [fill_opt(df.iloc[index][opt], df.iloc[index][opt.replace('Name', 'Value')]) for opt in opts]

            if (product_options[0] is not None) | (product_options[1] is not None) | (product_options[2] is not None):
                product_options = [x for x in product_options if x is not None]
                data_dict['input']['productOptions'] = product_options
            # data_dict['input']['productType'] = df.iloc[index]['Type']
            data_dict['input']['redirectNewHandle'] = str_to_bool('True')
            data_dict['input']['requiresSellingPlan'] = str_to_bool('False')
            data_dict['input']['seo'] = {'description': df.iloc[index]['SEO Description'],
                                         'title': df.iloc[index]['SEO Title']
                                         }
            data_dict['input']['status'] = df.iloc[index]['Status'].upper()
            data_dict['input']['tags'] = df.iloc[index]['Tags']
            # data_dict['input']['templateSuffix'] = ''
            data_dict['input']['title'] = df.iloc[index]['Title']
            data_dict['input']['vendor'] = df.iloc[index]['Vendor']

            media_list = [fill_media(literal_eval(df.iloc[index]['Link'])[i], literal_eval(df.iloc[index]['Image Alt Text'])[i]) for i in range(0, len(literal_eval(df.iloc[index]['Link'])))]
            data_dict['media'] = media_list
            datas.append(data_dict.copy())

    else:
        print('Mode value is not available')

    if datas:
        with open(jsonl_filename, 'w') as jsonlfile:
            for item in datas:
                json.dump(item, jsonlfile)
                jsonlfile.write('\n')

def merge_images(product_df: pd.DataFrame, image_df: pd.DataFrame):
    print('Merging images...')
    grouped_image_df = image_df.groupby('Handle')['Link'].agg(list).reset_index()
    print(grouped_image_df)
    result_df = product_df.merge(grouped_image_df, how='left', left_on='Handle', right_on='Handle')
    result_df.to_csv('data/create_products_with_images.csv', index=False)



if __name__ == '__main__':
    # to_shopify('data/All_Products_PWHSL.xlsx')

    product_df = pd.read_csv('data/create_products.csv')
    image_df = pd.read_csv('data/product_images.csv')
    merge_images(product_df, image_df=image_df)
    csv_to_jsonl()
