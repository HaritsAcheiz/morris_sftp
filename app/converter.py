from itertools import product
import pandas as pd
import re
import numpy as np
import json

def to_handle(title):
    if (pd.isna(title)) | (title == 0):
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


def generate_image(*args):
    image_urls = [x for x in list(args[0]) if str(x) != 'nan']
    if len(image_urls) == 0:
        return ''

    else:
        return image_urls


def generate_alt_text(*args):
    image_alt_text = [x.split('/')[-1].split('.')[0] for x in args[0]]
    if len(image_alt_text) == 0:
        return ''

    else:
        return image_alt_text


def to_shopify(morris_file_path):
    morris_df = pd.read_excel(morris_file_path)
    shopify_df = pd.DataFrame()
    shopify_df['Handle'] = morris_df['FormattedName'].apply(to_handle)
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
    shopify_df['Status'] = 'active'
    shopify_df.fillna('', inplace=True)
    # shopify_df.explode('')

    shopify_df.to_csv('./data/temp.csv', index=False)

def fill_opt(opt_name, opt_values):
    opt_attr = {'name': None, 'values': None}

    return opt_attr

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError

def csv_to_jsonl(csv_filename, jsonl_filename):
    print("Converting csv to jsonl file...")
    df = pd.read_csv(csv_filename, nrows=5)
    df.fillna('', inplace=True)

    # Create formatted dictionary
    datas = []
    for index in df.index:
        print(df.iloc[index]['Option1 Name'])
        data_dict = {"input": dict(), "media": dict()}
        # data_dict['input']['category'] = ''
        data_dict['input']['claimOwnership'] = {'bundles': str_to_bool('False')}
        # data_dict['input']['collectionToJoin'] = ''
        # data_dict['input']['collectionToLeave'] = ''
        data_dict['input']['combinedListingRole'] = 'PARENT'
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
        opts = ['Option1 Name', 'Option2 Name', 'Option3 Name']
        product_options = [fill_opt([df.iloc[index][opt]], df.iloc[index][opt.replace('Name', 'Value')]) for opt in opts if opt != '']
        print(product_options)
        # data_dict['input']['productOptions'] = [{#'linkedMetafields': '',
        #                                          'name': df.iloc[index]['Option1 Name'],
        #                                          # 'position': '',
        #                                          'values': df.iloc[index]['Option1 Value']},
        #                                         {#'linkedMetafields': '',
        #                                          'name': df.iloc[index]['Option2 Name'],
        #                                          #'position': '',
        #                                          'values': df.iloc[index]['Option2 Value']},
        #                                         {#'linkedMetafields': '',
        #                                          'name': df.iloc[index]['Option3 Name'],
        #                                          #'position': '',
        #                                          'values': df.iloc[index]['Option3 Value']}
        #                                        ]
        data_dict['input']['productOptions'] = product_options
        data_dict['input']['productType'] = df.iloc[index]['Type']
        data_dict['input']['redirectNewHandle'] = str_to_bool('False')
        data_dict['input']['requiresSellingPlan'] = str_to_bool('False')
        data_dict['input']['seo'] = {'description': df.iloc[index]['SEO Description'],
                                     'title': df.iloc[index]['SEO Title']
                                     }
        data_dict['input']['status'] = df.iloc[index]['Status'].upper()
        data_dict['input']['tags'] = df.iloc[index]['Tags']
        # data_dict['input']['templateSuffix'] = ''
        data_dict['input']['title'] = df.iloc[index]['Title']
        data_dict['input']['vendor'] = df.iloc[index]['Vendor']
        data_dict['media'] = {'originalSource': f"https:{df.iloc[index]['Image Src']}",
                              'mediaContentType': 'IMAGE',
                              'alt': list(df.iloc[index]['Image Alt Text'])[0]
                              }
        datas.append(data_dict.copy())

    print(datas)

    with open(jsonl_filename, 'w') as jsonlfile:
        for item in datas:
            json.dump(item, jsonlfile)
            jsonlfile.write('\n')

# draft
# data_dict['input']['productCategory'] = df.iloc[index]['Product Category']
#         # Convert symbol to unit
#         if df.iloc[index]['Variant Weight Unit'] == "g":
#             df.loc[index, 'Variant Weight Unit'] = "GRAMS"
#         elif df.iloc[index]['Variant Weight Unit'] == "kg":
#             df.loc[index, 'Variant Weight Unit'] = "KILOGRAMS"
#         elif df.iloc[index]['Variant Weight Unit'] == "lb":
#             df.loc[index, 'Variant Weight Unit'] = "POUNDS"
#         # Variant Attributes
#         data_dict['input']['variants'] = [
#             {'sku': df.iloc[index]['Variant SKU'],
#              'options': [
#                  df.iloc[index]['Option1 Value'],
#                  df.iloc[index]['Option2 Value'],
#                  df.iloc[index]['Option3 Value']
#              ],
#              'weight': int(df.iloc[index]['Variant Grams']),
#              'weightUnit': df.iloc[index]['Variant Weight Unit'],
#              'inventoryManagement': df.iloc[index]['Variant Inventory Tracker'].upper(),
#              'inventoryPolicy': df.iloc[index]['Variant Inventory Policy'].upper(),
#              'price': str(df.iloc[index]['Variant Price']),
#              'compareAtPrice': str(df.iloc[index]['Variant Compare At Price']),
#              'requiresShipping': bool(df.iloc[index]['Variant Requires Shipping']),
#              'taxable': bool(df.iloc[index]['Variant Taxable']),
#              'imageSrc': f"https:{df.iloc[index]['Image Src']}",
#              'title': 'Default'
#              }
#         ]


if __name__ == '__main__':
    to_shopify('./data/All_Products_PWHSL.xlsx')