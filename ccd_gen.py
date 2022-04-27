import paramiko
import os
from dotenv import load_dotenv
from netaddr import *
load_dotenv()
# network = IPNetwork('')

ccd_path = os.getenv('CCD_PATH')
hostname = os.getenv('SSH_HOST')
username = os.getenv("SSH_USERNAME")
password = os.getenv("SSH_PASSWORD")
ovpn_config_path = os.getenv('OPEN_VPN_CONFIG_FILE')
ssh_key_path = os.getenv("SSH_KEY_PATH")
print(ssh_key_path, username)
ssh_passphrase = os.getenv("SSH_PASSPHRASE")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=hostname, username=username, key_filename=ssh_key_path)
ssh = client.invoke_shell()

def add_user(username):

    _, stdout, _ = client.exec_command('cat {}'.format(ovpn_config_path))
    for line in stdout.read().decode().strip().split('\n'):
        if 'option server' in line:
            vpn_network, vpn_netmask = [i.strip("'") for i in line.split('server')[1].strip().split(' ')]
            break
    network = IPNetwork(f'{vpn_network}/{vpn_netmask}')
    _, stdout, _ =client.exec_command('cat {}*'.format(ccd_path))
    used_ips = []
    for i in stdout.read().decode().strip().split('\n'):
        used_ips.append(IPAddress(i.split(' ')[1]))
    all_ips = network[5::4]

    for ip in all_ips:
        if ip not in used_ips:
            curr_ip = ip
            break
    if 'curr_ip' in globals(): 
        print(f"User created with ip {curr_ip} route is {curr_ip+1}")
        print(f"ifconfig-push {curr_ip} {curr_ip+1}")
    else:
        raise ValueError("All addresess are used")



client.close()