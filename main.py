from sftp import connect_sftp, get_latest_files, download_file
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    hostname = os.getenv('MC_HOST')
    username = os.getenv('MC_USER')
    password = os.getenv('MC_PASS')
    remote_path = '/'
    local_path = 'D:/Naru/morris_sftp/'
    sftp = None

    # Download file from SFTP
    try:
        sftp = connect_sftp(hostname, username, password)

        latest_full_product, latest_inventory = get_latest_files(sftp, remote_path)

        if latest_full_product:
            download_file(sftp, os.path.join(remote_path, latest_full_product),
                          os.path.join(local_path, latest_full_product))
        else:
            print("No AvailableBatch_Full_Product_Data file found")

        if latest_inventory:
            download_file(sftp, os.path.join(remote_path, latest_inventory), os.path.join(local_path, latest_inventory))
        else:
            print("No AvailableBatch_Inventory_Only file found")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if sftp:
            sftp.close()