import paramiko
import os
from datetime import datetime


def connect_sftp(hostname, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, look_for_keys=False)
    return ssh.open_sftp()


def list_directory(sftp, remote_path):
    try:
        files = sftp.listdir(remote_path)
        print(f"Contents of {remote_path}:")
        for file in files:
            try:
                file_attr = sftp.stat(os.path.join(remote_path, file))
                file_type = 'D' if file_attr.st_mode & 0o40000 else 'F'
                print(f"{file_type} - {file}")
            except IOError:
                print(f"? - {file} (unable to get file information)")
    except IOError as e:
        print(f"Error listing directory {remote_path}: {str(e)}")


def download_file(sftp, remote_path, local_path):
    try:
        sftp.get(remote_path, local_path)
        print(f"File downloaded successfully to {local_path}")
    except IOError as e:
        print(f"Error downloading file: {str(e)}")


def get_latest_files(sftp, remote_path):
    files = sftp.listdir(remote_path)

    full_product_files = [f for f in files if f.startswith('AvailableBatch_Full_Product_Data_')]
    inventory_files = [f for f in files if f.startswith('AvailableBatch_Inventory_Only_')]

    if full_product_files:
        latest_full_product = max(full_product_files,
                                  key=lambda x: datetime.strptime('_'.join(x.split('_')[4:6]).split('.')[0], '%Y%m%d_%H%M%S'))
    else:
        latest_full_product = None

    if inventory_files:
        latest_inventory = max(inventory_files,
                               key=lambda x: datetime.strptime('_'.join(x.split('_')[3:5]).split('.')[0], '%Y%m%d_%H%M%S'))
    else:
        latest_inventory = None

    return latest_full_product, latest_inventory


def main():
    hostname = os.getenv('MC_HOST')
    username = os.getenv('MC_USER')
    password = os.getenv('MC_PASS')
    remote_path = '/'
    local_path = '/data/'
    sftp = None

    try:
        sftp = connect_sftp(hostname, username, password)

        latest_full_product, latest_inventory = get_latest_files(sftp, remote_path)
        os.makedirs('/data', exist_ok=True)
        if latest_full_product:
            download_file(sftp, os.path.join(remote_path, latest_full_product), os.path.join(local_path, latest_full_product))
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


if __name__ == "__main__":
    main()