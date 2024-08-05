import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

def main(argv=None):
    try:
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_system_host_keys()
            ssh.connect(os.getenv('MC_HOST'), username=os.getenv('MC_USER'), password=os.getenv('MC_PASS'))

            with ssh.open_sftp() as sftp:
                # remote_dir = 'public'  # Directory you want to browse
                local_dir = 'D:/Naru/morris_sftp/'  # Local directory to save files

                # Ensure local directory exists
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)

                # List files in remote directory
                remote_files = sftp.listdir()
                print(remote_files)
                #
                # print(f"Files in remote directory '{remote_dir}': {remote_files}")
                #
                # # Download each file
                # for file in remote_files:
                #     remote_file_path = os.path.join(remote_dir, file)
                #     local_file_path = os.path.join(local_dir, file)
                #
                #     try:
                #         sftp.get(remote_file_path, local_file_path)
                #         print(f"Downloaded {remote_file_path} to {local_file_path}")
                #     except Exception as e:
                #         print(f"Failed to download {remote_file_path}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()