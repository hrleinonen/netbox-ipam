#!/usr/bin/env python3
#
# Python script to collect IP-addresses from NetBox and check if IP is up
# and making reverse dns-lookup against IP's. Script automatically
# updates entry's DNS record.
#
# Tested NetBox versions v3.3.4 (date_time must be False) and v3.5.6
#
# Script requires custom_fields in NetBox, you can download cvs files here:
# 
# Author: Ville Leinonen
# Versio: 0.5
#
import urllib3
import json
import time
import requests
import dns.resolver, dns.reversename
from netbox import NetBox
from pythonping import ping

# Change if you want also resolve dead hosts (True/False).
resolve_dead = True

# Date and time supported in custom fields (True/False).
date_time = False

# NetBox API-token
token = "<API token>"

# NetBox connection settings
netbox_url = "<URL/IP>" # NetBox URL or IP eg. netbox.acme.dom
netbox_port = "<port>" # NetBox port eg. 8000
netbox_ssl = True # True if https is enabled, else False.

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {  
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Token ' + token + ''
}

netbox = NetBox(host=netbox_url, port=netbox_port, use_ssl=netbox_ssl, auth_token=token)

t = time.localtime()

json_data = netbox.ipam.get_ip_addresses()

for ipam_data in json_data:

   if date_time:
      current_time = time.strftime("%Y-%m-%d %H:%M:%S", t)
   else:
      current_time = time.strftime("%Y-%m-%d", t)

   id = ipam_data['id'] # Get entry id
   address = ipam_data['address'] # Get IP-address
   is_active = ipam_data['status']['value'] # Check if IP-address is active or dhcp
   address_url = ipam_data['url'] # Get device id
   seen_enabled = ipam_data['custom_fields']['seen_enabled'] # Check if ping is enabled
   dns_enabled = ipam_data['custom_fields']['dns_enabled'] # Check if DNS-lookup is enabled
   first_seen = ipam_data['custom_fields']['first_seen'] # Get first seen value

   address = address.split('/')

   if is_active == "active" and seen_enabled == True:

      # Do the ping against host
      response_list = ping(address[0], count=3, timeout=2)

      # If host id down
      if str(response_list.rtt_avg_ms) == "2000.0":
         seen_data = { "custom_fields": {
            "host_alive" : False
         }}
   
         host_up = False

      # If host is up
      else:
         # If host is not checked before and it is online
         if not first_seen:
            seen_data = { "custom_fields": {
               "first_seen" : current_time,
               "host_alive" : True,
               "last_seen" : current_time
            }}
         else:
            seen_data = { "custom_fields": {
               "host_alive" : True,
               "last_seen" : current_time
            }}

         host_up = True

      r = requests.patch(address_url, headers=headers, json=seen_data, verify=False)

      # Check if DNS-entry is automaticly updated.
      if dns_enabled == True:

         if resolve_dead:

            addrs = dns.reversename.from_address(address[0])

            try:
               dns_name = str(dns.resolver.resolve(addrs,"PTR")[0])
               if dns_name[-1] == '.':
                  dns_name = dns_name.rstrip(dns_name[-1])

               dns_data = {
                  "dns_name" : str(dns_name)
               }
               r = requests.patch(address_url, headers=headers, json=dns_data, verify=False)
            except:
               pass

         elif not resolve_dead and host_up:

            addrs = dns.reversename.from_address(address[0])
         
            try:
               dns_name = str(dns.resolver.resolve(addrs,"PTR")[0])
               if dns_name[-1] == '.':
                  dns_name = dns_name.rstrip(dns_name[-1])
              
               dns_data = {
                  "dns_name" : str(dns_name)
               }
               r = requests.patch(address_url, headers=headers, json=dns_data)
            except:
               pass
