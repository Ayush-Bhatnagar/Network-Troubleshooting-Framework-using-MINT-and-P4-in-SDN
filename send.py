#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import time

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

ipToMac = {"10.0.1.1" : "08:00:00:00:01:11", "10.0.2.2" : "08:00:00:00:02:22", "10.0.3.3" : "08:00:00:00:03:33", "10.0.4.4" : "08:00:00:00:04:44"}

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
    args = parser.parse_args()
    addr = socket.gethostbyname(args.ip_addr)
    mac_addr = ipToMac[args.ip_addr]
    #message = "This is a dummy txt message sent from one host to another for MINT show"
    iface = get_if()

    eth = Ether(src=get_if_hwaddr(iface), dst=mac_addr)
    pkt = eth / IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / args.message
    
    #i=1;
    #while i<=5:
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
    #time.sleep(1)
    #i=i+1

if __name__ == '__main__':
    main()
