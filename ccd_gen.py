import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

ccd_path = os.getenv('CCD_PATH')
hostname = os.getenv('SSH_HOST')
username = os.getenv("SSH_USERNAME")
password = os.getenv("SSH_PASSWORD")
ssh_key_path = os.getenv("SSH_KEY_PATH")
ssh_passphrase = os.getenv("SSH_PASSPHRASE")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=hostname, username=username, key_filename=ssh_key_path)
ssh = client.invoke_shell()
client.exec_command('cat {}'.format(ccd_path))
ssh.close()