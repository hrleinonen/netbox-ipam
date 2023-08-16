#!/usr/bin/env python3
#
# Python script to scan IP-address ranges and add active IP's NetBox.
# <---- Reverse is not working yet --->
# Script also make reverse dns-lookup against IP's. Script automatically
# updates entry's DNS record.
#
# Tested NetBox version v3.5.6
#
#
# Usage 1: netbox-scan.py --networks 192.168.0.0/24 --url http://127.0.0.1:8000 --api asdasdasf12222 
# Usage 2: netbox-scan.py --networks 192.168.0.0/24,10.20.0.0/23 --url http://127.0.0.1:8000 --api asdasdasf12222
#
# Author: Ville Leinonen
# Version: 0.1
#
import os
import urllib3
import json
import time
import requests
import dns.resolver, dns.reversename
from netbox import NetBox
from ping3 import ping
from dotenv import load_dotenv

import argparse
import ipaddress

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser()
parser.add_argument('--networks', type=str, nargs='+', required=True)
parser.add_argument('--url', type=str, required=True)
parser.add_argument('--api', type=str, required=True)
parser.add_argument('--dns', action='store_true')

args = parser.parse_args()

networks = args.networks
url = args.url
token = args.api
dns = args.dns

headers = {  
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Token ' + token + ''
}

# Get all ip's for duplicate check
try:
   r = requests.get(str(url) + "/api/ipam/ip-addresses", headers=headers, verify=False)
except:
   print("Error to connect {}.".format(url))
   exit()

json_data = r.json()

ip_array = [] 

for json_items in json_data['results']:
   for key, val in json_items.items():
      if key == "address":
         ip = val
         ip = ip.split('/')
         
   ip_array.append(ip[0])

for network in networks:
   network = network.replace(',','')
   netmask = network.split('/')
   netmask = netmask[1]

   ips = ipaddress.ip_network(network, strict=False)
   for ip in ips:

      t = time.localtime()

      current_time = time.strftime("%Y-%m-%d %H:%M:%S", t)

      ip_mask = str(ip) + "/" + str(netmask)

      ip_mask = ip_mask.strip()

      # Do the ping against host
      try:
         ip_response = ping(str(ip), timeout=1)

         if ip_response is not None:
            if str(ip) not in ip_array:
               comment = str("Created automatically " + current_time + ".")
               ip_data = {
                     "address": ip_mask,
                     "status": "active",
                     "comments": comment
                  }
               r = requests.post(str(url) + "/api/ipam/ip-addresses/", headers=headers, json=ip_data, verify=False)
          
               resp = r.json()

               for resp_key, resp_val in resp.items():
                  if resp_key == "url":
                     print(resp_val)
                     address_url = str(resp_val)

               # Check if DNS lookup required.
               if dns == True:

                  ip_addrs = str(ip).strip()

                  addrs = dns.reversename.from_address(ip_addrs)
         
                  try:
                     dns_name = str(dns.resolver.resolve(addrs,"PTR")[0])
                     if dns_name[-1] == '.':
                        dns_name = dns_name.rstrip(dns_name[-1])
               
                        dns_data = {
                           "dns_name" : str(dns_name)
                        }
                        r = requests.patch(address_url, headers=headers, json=dns_data, verify=False)
                  except:
                     print("No reverse DNS in {}".format(ip))
                  
            else:
               print("IP {} is allready in NetBox".format(ip))

         else:
            print("Address {} not responding.".format(ip_mask))

      except:
         print("Error pinging {}".format(ip_mask))
