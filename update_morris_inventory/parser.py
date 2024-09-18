import pandas as pd

def convert_to_shopify(file_path, file_type):
    df = pd.read_xml(file_path, xpath='//available')
    if file_type == 'full':
        # df.drop(columns=['AvailableBatch', 'Type', 'Date', 'available', 'activeStatus', 'code', 'baggable'])
        df.iloc[:, range(len(df.columns))].to_csv('full_template.csv', index=False)
    elif file_type == 'inventory':
        df.iloc[:, range(len(df.columns))].to_csv('inventory_template.csv', index=False)
