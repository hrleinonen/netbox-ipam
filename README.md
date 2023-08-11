# netbox-ipam

Python script to collect IP-addresses from NetBox and check if IP is up
and making reverse dns-lookup against IP's. Script automatically
updates entry's DNS record.

![Example output](https://github.com/hrleinonen/netbox-ipam/blob/main/pictures/NetBox_funet.png)

Managing IP addresses is great, but maintaining documentation is a pain. Someone deletes the device but doesn't delete its data. DNS records are also not always clear. I coded this script to alleviate these problems.

The script searches the NetBox API for IP addresses that are marked with "alive" status and ping them, after that it updates the IP address information about whether the IP is up or not and when it was last up. The script also updates the information because the IP has been up for the first time.

The script also performs a reverse DNS query for IP addresses and updates the information in the DNS field.

You must create custom_fields in NetBox, please check netbox_custom_date.csv and netbox_custom_datetime.cvs files. If your NetBox version supports datetime format in custom fields, then use netbox_custom_datetime.cvs file.

API-needs readwrite perssion in NetBox.

Screenshot from Customization > Custom Fields (Import netbox_custom_datetime.cvs should be something like this):

![Example output](https://github.com/hrleinonen/netbox-ipam/blob/main/pictures/NetBox_customfields.png)

Screenshot from new IP.

![Example output](https://github.com/hrleinonen/netbox-ipam/blob/main/pictures/NetBox_New_IP.png)
