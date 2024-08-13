from sftp import connect_sftp, get_latest_files, download_file, list_directory
import os
from dotenv import load_dotenv
from parser import convert_to_shopify

load_dotenv()

if __name__ == '__main__':
    hostname = os.getenv('MC_HOST')
    username = os.getenv('MC_USER')
    password = os.getenv('MC_PASS')
    remote_path = '/'
    local_path = '/data/'
    sftp = None

    # Download file from SFTP

    try:
        sftp = connect_sftp(hostname, username, password)

    # Get list of file
        list_directory(sftp, remote_path=remote_path)

    # Get latest file
    #     latest_full_product, latest_inventory = get_latest_files(sftp, remote_path)
    #     os.makedirs('D:/Naru/morris_sftp/data', exist_ok=True)
    #     if latest_full_product:
    #         download_file(sftp, os.path.join(remote_path, latest_full_product),
    #                       os.path.join(local_path, latest_full_product))
    #     else:
    #         print("No AvailableBatch_Full_Product_Data file found")
    #
    #     if latest_inventory:
    #         download_file(sftp, os.path.join(remote_path, latest_inventory), os.path.join(local_path, latest_inventory))
    #     else:
    #         print("No AvailableBatch_Inventory_Only file found")
    #
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if sftp:
            sftp.close()

    # hardcode path to test
    # full_product_path = 'D:/Naru/morris_sftp/data/AvailableBatch_Full_Product_Data_20240807_225146.xml'
    # inventory_path = 'D:/Naru/morris_sftp/data/AvailableBatch_Inventory_Only_20240808_012053.xml'

    # Parse xml file and convert to shopify template
    # try:
        # full_product_path = os.path.join(local_path, latest_full_product)
        # full_product_src = parse_xml(full_product_path, file_type='full')
        # inventory_path = os.path.join(local_path, latest_inventory)
        # inventory_src = parse_xml(inventory_path, file_type='inventory')
        # convert_to_shopify(file_path=full_product_path, file_type='full')
        # convert_to_shopify(file_path=inventory_path, file_type='inventory')
    # except FileNotFoundError as e:
    #     print(e)




