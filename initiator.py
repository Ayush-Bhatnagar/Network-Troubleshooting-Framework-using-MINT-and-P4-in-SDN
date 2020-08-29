#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
from custom_headers import *

ipToLabel = { "10.0.1.1" : 1, "10.0.2.2" : 2, "10.0.3.3" : 3, "10.0.4.4" : 4, "10.0.5.5" : 5}
ipToMac = {"10.0.1.1" : "08:00:00:00:01:11", "10.0.2.2" : "08:00:00:00:02:22", "10.0.3.3" : "08:00:00:00:03:33", "10.0.4.4" : "08:00:00:00:04:44", "10.0.5.5" : "08:00:00:00:05:55"}

def expand(x):
    print x.name
    while x.payload:
        x = x.payload
        print x.name


def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', type=str, help="The destination IP address to use")
    parser.add_argument('message', type=str, help="The message to include in packet")
    parser.add_argument('mint', type=str, help="To enable MINT")
    args = parser.parse_args()
    addr = socket.gethostbyname(args.ip_addr)
    label = ipToLabel[args.ip_addr]
    mac_addr = ipToMac[args.ip_addr]
    iface = get_if()

    if (args.mint == 'False'):
	eth = Ether(src=get_if_hwaddr(iface), dst=mac_addr, type=TYPE_MPLS)
	mpls_lables = mpls(label_id=label, tc=0, bos=1, ttl=255)
	pkt = eth / mpls_lables / IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / args.message

    else:
        eth = Ether(src=get_if_hwaddr(iface), dst=mac_addr, type=TYPE_MPLS)
        pkt = eth / mpls(label_id=label, tc=0, bos=0, ttl=255) / mpls(label_id=15, tc=0, bos=0, ttl=255) / mpls(label_id=16, tc=0, bos=1, ttl=255) / IP(dst=addr, proto=PROTOCOL_MINT) / mint_hdr(gns=1, next_header=PROTOCOL_TCP) / TCP(dport=1234, sport=random.randint(49152,65535)) / mint_metadata_hdr() / mint_metadata() / mint_metadata() / mint_metadata() / args.message

    pkt.show2();
    #expand(pkt)
    sendp(pkt, iface=iface, verbose=False)

if __name__ == '__main__':
    main()
