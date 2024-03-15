# Imported according to the jupyter providers manual.
# For more information see the Jira ticket FU-69
import netifaces as ni
from scapy.all import ARP, Ether, srp
from ipaddress import ip_network
import subprocess


def get_network_range(interface='eth0'):
    addr = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
    netmask = ni.ifaddresses(interface)[ni.AF_INET][0]['netmask']
    network = ip_network(f"{addr}/{netmask}", strict=False)
    return str(network)


def scan_network(ip_range):
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    devices = []
    for sent, received in answered_list:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    return devices


default_interface = ni.gateways()['default'][ni.AF_INET][1]
network_range = get_network_range(default_interface)
devices = scan_network(network_range)
device_string=""

for device in devices:
    device_string += f"IP Address: {device['ip']}, MAC Address: {device['mac']}\n"

binary_path="./myBinary"

process = subprocess.Popen([binary_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate(input=device_string)

print(stdout)