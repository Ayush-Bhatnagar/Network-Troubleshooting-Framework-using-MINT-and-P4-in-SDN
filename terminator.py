#!/usr/bin/env python

import sys
from custom_headers import *

collector_ip = "10.0.2.15"

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

def expand(x):
    print x.name
    yield x
    while x.payload:
        x = x.payload
        print x.name
        yield x

def send_data_to_collector(data):
	print "Connecting to collector"
	addr = collector_ip
    	iface = get_if()
    	print "sending on interface %s to %s" % (iface, str(addr))
    	pkt2 =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    	pkt3 = pkt2 /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / data
    	sendp(pkt3, verbose=False)


def handle_pkt(pkt):
	mint_data = ""
	if IP in pkt:
		src_ip = pkt.getlayer(IP).src
		dst_ip = pkt.getlayer(IP).dst
		if dst_ip != collector_ip:
			split_layers(TCP, mint_metadata_hdr)
			split_layers(UDP, mint_metadata_hdr)			
			pkt.show2()
			if pkt.getlayer(IP).proto == PROTOCOL_MINT:
				bind_layers(TCP, mint_metadata_hdr)
				bind_layers(UDP, mint_metadata_hdr)
				bind_layers(mint_metadata_hdr, mint_metadata)
				bind_layers(mint_metadata, mint_metadata, bos=0)
				bind_layers(mint_metadata, Raw, bos=1)
				src_port = pkt.getlayer(TCP).sport
				dst_port = pkt.getlayer(TCP).dport
				mint_data = mint_data + "src_ip: {}, dst_ip: {}, src_port: {}, dst_port: {} \n".format(src_ip, dst_ip, src_port, dst_port)
        			metadata = [layer for layer in expand(pkt) if layer.name=='mint_metadata']
        			for data in metadata:
					mint_data = mint_data + "switch_id: {}, deque_timedelta: {}, enque_qdepth: {}, delay_at_switch: {}, ingress_port: {}, egress_port: {} \n".format(data.switch_id, data.deq_timedelta, data.enq_qdepth, data.delay_at_switch, data.ingress_port, data.egress_port)
        			print "Data Extracted and sending it to collector " + mint_data
				send_data_to_collector(mint_data)


def main():
    iface = "eth0"
    print "sniffing on %s" % iface
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
