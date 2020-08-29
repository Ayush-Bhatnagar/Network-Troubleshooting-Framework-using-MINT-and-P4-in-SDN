#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import argparse, grpc, os, sys
from time import sleep
from scapy.all import *

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
        '../../utils/'))

import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

def writeTunnelRules(p4info_helper, sw, label_id, port):
    table_entry = p4info_helper.buildTableEntry(
        table_name = "MyIngress.label_match",
        match_fields = {
            "hdr.mpls[0].label_id": label_id
        },
        action_name = "MyIngress.tunnel_forward",
        action_params = {
            "port" : port
        })
    sw.WriteTableEntry(table_entry)

def setSwitchId(p4info_helper, sw, switch_id):
    table_entry = p4info_helper.buildTableEntry(
        table_name = "MyEgress.switch_id",
        match_fields = {},
        action_name = "MyEgress.set_switch_id",
        action_params = {
            "switch_id" : switch_id
        })
    sw.WriteTableEntry(table_entry)


def writeMint(p4info_helper, sw, status):
    table_entry = p4info_helper.buildTableEntry(
        table_name = "MyIngress.mint_status",
        match_fields = {},
        action_name = "MyIngress.enable_mint",
        action_params = {
            "status_bit" : status
        })
    sw.WriteTableEntry(table_entry)


def updateMint(p4info_helper, sw, status):
    table_entry = p4info_helper.buildTableEntry(
        table_name = "MyIngress.mint_status",
        match_fields = {},
        action_name = "MyIngress.enable_mint",
        action_params = {
            "status_bit" : status
        })
    sw.ModifyTableEntry(table_entry)



def defineLabels(p4info_helper, sw, dstAddr, label_id):
    table_entry = p4info_helper.buildTableEntry(
        table_name = "MyIngress.attach_label",
        match_fields = {
            "hdr.ipv4.dstAddr": (dstAddr, 32)
        },
        action_name = "MyIngress.set_label",
        action_params = {
            "label" : label_id
        })
    sw.WriteTableEntry(table_entry)


def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    # - then need to read from the file compile from P4 Program, which call .p4info
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)
    
    # Live and static server constants
    label_for_live_server = 1;
    label_for_static_server = 2;    
    live_server_ip = "10.0.3.3";
    static_server_ip = "10.0.4.4";

    try:
        
        # Establishing connection with switches
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')

	s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')

	s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s1-p4runtime-requests.txt')

	s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
            proto_dump_file='logs/s1-p4runtime-requests.txt')

	s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s5',
            address='127.0.0.1:50055',
            device_id=4,
            proto_dump_file='logs/s1-p4runtime-requests.txt')

        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
	s2.MasterArbitrationUpdate()
	s3.MasterArbitrationUpdate()
	s4.MasterArbitrationUpdate()
	s5.MasterArbitrationUpdate()

        # P4 switch
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s1"


	s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s2"


	s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s3"


	s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s4"


	s5.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForardingPipelineConfig on s5"


	## Gateway Switch S1 defining labels for incoming traffic
	defineLabels(p4info_helper, sw=s1, dstAddr=live_server_ip, label_id=label_for_live_server);
	defineLabels(p4info_helper, sw=s1, dstAddr=static_server_ip, label_id=label_for_static_server);
	writeTunnelRules(p4info_helper, sw=s1 , label_id=1, port=2);
	writeTunnelRules(p4info_helper, sw=s1 , label_id=2, port=3);
	setSwitchId(p4info_helper, sw=s1, switch_id=1);
	writeMint(p4info_helper, sw=s1, status=0);
	print "Installed tunnel rules on switch s1 and set the switch id as 1"

	writeTunnelRules(p4info_helper, sw=s2 , label_id=1, port=3);
	writeTunnelRules(p4info_helper, sw=s2 , label_id=2, port=4);
	setSwitchId(p4info_helper, sw=s2, switch_id=2);
	writeMint(p4info_helper, sw=s2, status=0);
	print "Installed tunnel rules on switch s2 and set the switch id as 2"
	
	## Gateway Switch S3 defining labels for incoming traffic
	defineLabels(p4info_helper, sw=s3, dstAddr=live_server_ip, label_id=label_for_live_server);
	defineLabels(p4info_helper, sw=s3, dstAddr=static_server_ip, label_id=label_for_static_server);	
	writeTunnelRules(p4info_helper, sw=s3 , label_id=1, port=2);
	writeTunnelRules(p4info_helper, sw=s3 , label_id=2, port=3);
	setSwitchId(p4info_helper, sw=s3, switch_id=3);
	writeMint(p4info_helper, sw=s3, status=0);
	print "Installed tunnel rules on switch s3 and set the switch id as 3"


	writeTunnelRules(p4info_helper, sw=s4 , label_id=1, port=1);
	writeTunnelRules(p4info_helper, sw=s4 , label_id=2, port=4);
	setSwitchId(p4info_helper, sw=s4, switch_id=4);
	writeMint(p4info_helper, sw=s4, status=0);
	print "Installed tunnel rules on switch s4 and set the switch id as 4"


	writeTunnelRules(p4info_helper, sw=s5 , label_id=1, port=2);
	writeTunnelRules(p4info_helper, sw=s5 , label_id=2, port=1);
	setSwitchId(p4info_helper, sw=s5, switch_id=5);
	writeMint(p4info_helper, sw=s5, status=0);
	print "Installed tunnel rules on switch s5 and set the switch id as 5"

	status = 0
	while True:
		if status == 1:
			status = input("Press 0 to Stop the MINT process")
		else:
			status = input("Press 1 to Start the MINT process")
		updateMint(p4info_helper, sw=s1, status=status)
		updateMint(p4info_helper, sw=s2, status=status)
		updateMint(p4info_helper, sw=s3, status=status)
		updateMint(p4info_helper, sw=s4, status=status)
		updateMint(p4info_helper, sw=s5, status=status)

    except KeyboardInterrupt:
        # using ctrl + c to exit
        print "Shutting down."

    # Then close all the connections
    ShutdownAllSwitchConnections()



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
            type=str, action="store", required=False,
            default="./build/mint.p4.p4info.txt")
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
            type=str, action="store", required=False,
            default="./build/mint.json")
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print "\np4info file not found: %s\nPlease compile the target P4 program first." % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nPlease compile the target P4 program first." % args.bmv2_json
        parser.exit(1)

    # Pass argument into main function
    main(args.p4info, args.bmv2_json)
