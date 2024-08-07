import xml.etree.ElementTree as ET

def parse_xml(file_path, file_type):
    if file_type == 'full':
        root = ET.parse(file_path)
        parsed_dict = dict()
        for child in root.iter():
            if child.text:
                parsed_dict[child.tag] = child.text
            print(parsed_dict)
    elif file_type == 'inventory':
        root = ET.parse(file_path)
        parsed_dict = dict()
        for child in root.iter():
            if child.text:
                parsed_dict[child.tag] = child.text
            print(parsed_dict)

if __name__ == '__main__':
    parse_xml('D:\\Naru\\morris_sftp\\AvailableBatch_Full_Product_Data_20240806_225113.xml', file_type='full')
