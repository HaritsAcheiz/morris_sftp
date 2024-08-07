import xml.etree.ElementTree as ET
from pyairtable import Api
from dotenv import load_dotenv
import os
from dataclasses import dataclass

load_dotenv()

@dataclass
class AirtableAPI:
    api: Api = None

    def parse_xml(self, file_path, file_type):
        items = list()
        new_item = dict()
        if file_type == 'full':
            root = ET.parse(file_path)
            for child in root.iter():
                if child.text:
                    new_item[child.tag] = child.text
                    items.append(new_item)
        elif file_type == 'inventory':
            root = ET.parse(file_path)
            for child in root.iter():
                if child.text:
                    new_item[child.tag] = child.text
                    items.append(new_item)
        return items

    def authenticate(self, token):
        self.api = Api(token)


    def to_airtable(self, base_id, table_name):
        table = self.api.table(base_id, table_name=table_name)
        result = table.all()
        print(result)


if __name__ == '__main__':
    # items = parse_xml('D:\\Naru\\morris_sftp\\AvailableBatch_Full_Product_Data_20240806_225113.xml', file_type='full')
    # print(items)
    # parse_xml('D:\\Naru\\morris_sftp\\AvailableBatch_Inventory_Only_20240807_012058.xml', file_type='inventory')

    # Airtable
    api = AirtableAPI()
    api.authenticate(os.getenv('AIRTABLE_TOKEN'))
    api.to_airtable('app3Ilt72ww0tN04k', table_name='full_products')