#!/usr/bin/env python
import sys
import struct
import os
import json
import calendar
import time

from scapy.all import sniff, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import IP, TCP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR


def write_entries(entries, target_list):
    entries.pop(0)
    entries.pop(len(entries)-1)
    for entry in entries:
	mint_info = {}
	mint_items = entry.split(",")
	for item in mint_items:
		key = item.split(":")[0].strip()
		value = item.split(":")[1].strip()
		mint_info[key] = value
    	target_list.append(mint_info)


def dump_data(data):
    with open('mint_data.json', 'r+') as json_file:
    	data_list = json.load(json_file)
    	entries = data.split("\n")
    	json_keys = entries[0].split(",")
    	src_ip = json_keys[0].split(":")[1].strip()
    	dst_ip = json_keys[1].split(":")[1].strip()
    	src_port = json_keys[2].split(":")[1].strip()
    	dst_port = json_keys[3].split(":")[1].strip()
	ts = calendar.timegm(time.gmtime())
	flag = 0;
	for data_list_item in data_list:
		if data_list_item.has_key(dst_ip):
			if data_list_item[dst_ip].has_key(src_ip):
				data_list_item[dst_ip][src_ip][ts] = []
				write_entries(entries, data_list_item[dst_ip][src_ip][ts])

			else:
				data_list_item[dst_ip][src_ip] = {}
				data_list_item[dst_ip][src_ip][ts] = []
				write_entries(entries, data_list_item[dst_ip][src_ip][ts])
			flag = 1

	if flag == 0:
		json_obj = {}
    		json_obj[dst_ip] = {}			
    		json_obj[dst_ip][src_ip] = {}
    		json_obj[dst_ip][src_ip][ts] = []
		write_entries(entries, json_obj[dst_ip][src_ip][ts])
		data_list.append(json_obj)

	json_file.seek(0)
	json.dump(data_list, json_file)
    	print "Collecting data for packet from Source IP: {} Destination IP: {}".format(src_ip, dst_ip)
           

def handle_pkt(pkt):
    if TCP in pkt and pkt[TCP].dport == 1234:
        #pkt.show2()
    	dump_data(pkt.getlayer(TCP).payload.load)
        sys.stdout.flush()

def initialize_data_file():
    if not os.path.isfile('mint_data.json'):
    	data_list = []
    	with open('mint_data.json', 'w') as json_file:
    		json.dump(data_list, json_file)

def main():
    initialize_data_file()
    n = os.fork() 
    if n > 0:
    	ifaces = filter(lambda i: 's4-eth1' in i, os.listdir('/sys/class/net/'))
    	iface = ifaces[0]
    	print "sniffing for packets from live server"
    	sys.stdout.flush()
    	sniff(iface = iface,prn = lambda x: handle_pkt(x))

    else:
	ifaces = filter(lambda i: 's5-eth1' in i, os.listdir('/sys/class/net/'))
    	iface = ifaces[0]
    	print "sniffing for packets from static server"
    	sys.stdout.flush()
    	sniff(iface = iface,prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
