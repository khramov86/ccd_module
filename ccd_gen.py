import paramiko
import os
from dotenv import load_dotenv
from netaddr import *
import yaml


ccd_path = os.getenv('CCD_PATH')
hostname = os.getenv('SSH_HOST')
username = os.getenv("SSH_USERNAME")
password = os.getenv("SSH_PASSWORD")
ovpn_config_path = os.getenv('OPEN_VPN_CONFIG_FILE')
ssh_key_path = os.getenv("SSH_KEY_PATH")
ssh_passphrase = os.getenv("SSH_PASSPHRASE")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=hostname, username=username, key_filename=ssh_key_path)
ssh = client.invoke_shell()


def check_user_file(username):
    _, stdout, _ = client.exec_command('cat {}/{}'.format(ccd_path, username))
    if stdout.channel.recv_exit_status() == 1:
        return False
    return True

def add_user(username):
    if check_user_file(username):
        print(f"Static ip exists for user {username}")
        return
    _, stdout, _ = client.exec_command('cat {}'.format(ovpn_config_path))
    for line in stdout.read().decode().strip().split('\n'):
        if 'option server' in line:
            vpn_network, vpn_netmask = [i.strip("'") for i in line.split('server')[1].strip().split(' ')]
            break
    network = IPNetwork(f'{vpn_network}/{vpn_netmask}')
    _, stdout, _ =client.exec_command('cat {}/*'.format(ccd_path))
    used_ips = []
    for i in stdout.read().decode().strip().split('\n'):
        used_ips.append(IPAddress(i.split(' ')[1]))
    all_ips = network[5::4]

    for ip in all_ips:
        if ip not in used_ips:
            curr_ip = ip
            break
    print(f'{ovpn_config_path}/{username}')
    _, _, _ = client.exec_command(f'echo "ifconfig-push {curr_ip} {curr_ip+1}" > {ccd_path}/{username}')
    if 'curr_ip' in locals(): 
        print(f"User created with ip {curr_ip} route is {curr_ip+1}")
    else:
        raise ValueError("All addresess are used")

def parse_users(filename):
    with open(filename) as file:
        user_list = yaml.safe_load(file)['user_list']
    for user in user_list:
        add_user(user['username'])



if __name__ == '__main__':
    parse_users('users.yml')
    client.close()