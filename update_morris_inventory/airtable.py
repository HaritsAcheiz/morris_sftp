from pyairtable import Api
from dotenv import load_dotenv
import os
from dataclasses import dataclass

load_dotenv()

@dataclass
class AirtableAPI:
    api: Api = None
    base_id: str = 'app3Ilt72ww0tN04k'
    table_name = 'full_products'


    def authenticate(self, token):
        self.api = Api(token)


    def select_table(self, base_id=None, table_name=None):
        if base_id:
            self.base_id = base_id
        if table_name:
            self.table_name = table_name
        self.table = self.api.table(self.base_id, table_name=self.table_name)


if __name__ == '__main__':
    # items = parse_xml('D:\\Naru\\morris_sftp\\AvailableBatch_Full_Product_Data_20240806_225113.xml', file_type='full')
    # print(items)
    # parse_xml('D:\\Naru\\morris_sftp\\AvailableBatch_Inventory_Only_20240807_012058.xml', file_type='inventory')

    # Airtable
    api = AirtableAPI()
    api.authenticate(os.getenv('AIRTABLE_TOKEN'))

    # Select Table
    api.select_table()

    # Read all table
    api.table.cre
