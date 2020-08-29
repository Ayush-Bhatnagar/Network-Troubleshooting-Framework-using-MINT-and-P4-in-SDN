#!/usr/bin/env python
import sys
import os
import json

def get_attribute_from_json(src_ip, dst_ip, packets_count, attribute):
    with open('mint_data.json', 'r') as json_file:
    	data_list = json.load(json_file)
	ret_data = []   	
        count = 1;
   	for data_list_item in data_list:
		if data_list_item.has_key(dst_ip):
			if data_list_item[dst_ip].has_key(src_ip):
				packet_ids = data_list_item[dst_ip][src_ip].keys()
				packet_ids.reverse()
				for packet_id in packet_ids:
					if count > packets_count:
						break
					else:
						print "Packet {}:".format(count)
						count = count + 1
						packet_data_list = data_list_item[dst_ip][src_ip][packet_id]
						packet_data_list.reverse()
						for packet_data_list_item in packet_data_list:
							if attribute == "switch_id":
								print "	At switch: {}".format(packet_data_list_item[attribute])
							elif attribute == "deque_timedelta":
								print "	At switch: {}, 	Queuing Delay: {}".format(packet_data_list_item["switch_id"], packet_data_list_item[attribute])
							elif attribute == "enque_qdepth":
								print "	At switch: {}, 	Queue Depth: {}".format(packet_data_list_item["switch_id"], packet_data_list_item[attribute])
							elif attribute == "delay_at_switch":
								print "	At switch: {}, 	Delay at Switch: {}".format(packet_data_list_item["switch_id"], packet_data_list_item[attribute])					
			else:
				print "No data found for Source Ip: {}".format(src_ip)

	if len(data_list) == 0:
		print("No data found")
												

def sanitize_packets_count(packets_count):	
	try:
		packets_count = int(packets_count)
		if packets_count < 0:
			packets_count = 5
	except:
		packets_count = 5

	return packets_count


def get_network_ports():
    ports_flag = {}
    ports_flag["s1"] = {}
    ports_flag["s1"][1] = False
    ports_flag["s1"][2] = False
    ports_flag["s1"][3] = False
    ports_flag["s2"] = {}
    ports_flag["s2"][1] = False
    ports_flag["s2"][2] = False
    ports_flag["s2"][3] = False
    ports_flag["s2"][4] = False
    ports_flag["s3"] = {}
    ports_flag["s3"][1] = False
    ports_flag["s3"][2] = False
    ports_flag["s3"][3] = False
    ports_flag["s4"] = {}
    ports_flag["s4"][1] = False
    ports_flag["s4"][2] = False
    ports_flag["s4"][3] = False
    ports_flag["s4"][4] = False
    ports_flag["s5"] = {}
    ports_flag["s5"][1] = False
    ports_flag["s5"][2] = False
    ports_flag["s5"][3] = False
    ports_flag["s5"][4] = False
    return ports_flag


def get_packet_route():
    dst_ip = input("Enter the destination ip of packets")
    src_ip = input("Enter the source ip of packets")
    packets_count = input("Enter the no of packtes for inspecting")
    packets_count = sanitize_packets_count(packets_count)
    get_attribute_from_json(src_ip, dst_ip, packets_count, "switch_id")
        
def get_queuing_delay():
    dst_ip = input("Enter the destination ip of packets")
    src_ip = input("Enter the source ip of packets")
    packets_count = input("Enter the no of packtes for inspecting")
    packets_count = sanitize_packets_count(packets_count)
    get_attribute_from_json(src_ip, dst_ip, packets_count, "deque_timedelta")

def get_queue_depth():
    dst_ip = input("Enter the destination ip of packets")
    src_ip = input("Enter the source ip of packets")
    packets_count = input("Enter the no of packtes for inspecting")
    packets_count = sanitize_packets_count(packets_count)
    get_attribute_from_json(src_ip, dst_ip, packets_count, "enque_qdepth")

def get_switch_delay():
    dst_ip = input("Enter the destination ip of packets")
    src_ip = input("Enter the source ip of packets")
    packets_count = input("Enter the no of packtes for inspecting")
    packets_count = sanitize_packets_count(packets_count)
    get_attribute_from_json(src_ip, dst_ip, packets_count, "delay_at_switch")

def get_allowed_packet_routes():
    gateway_switch1_live = ['s1','s2','s4']
    gateway_switch2_live = ['s3','s4']
    gateway_switch1_static = ['s1','s5']
    gateway_switch2_static = ['s3','s2', 's5']
    separator = " -> "
    print "Path from Gateway Switch 1 (switch_id = 1) to live server (10.0.3.3)"
    print separator.join(gateway_switch1_live)

    print "Path from Gateway Switch 2 (switch_id = 3) to live server (10.0.3.3)"
    print separator.join(gateway_switch2_live)

    print "Path from Gateway Switch 1 (switch id = 1) to static server (10.0.4.4)"
    print separator.join(gateway_switch1_static)

    print "Path from Gateway Switch 2 (switch id = 3) to static server (10.0.4.4)"
    print separator.join(gateway_switch2_static)


def get_working_switch_ports():
    #import pdb; pdb.set_trace()
    packets_count = input("Enter the no of packtes for inspecting")
    packets_count = sanitize_packets_count(packets_count)
    with open('mint_data.json', 'r') as json_file:
    	data_list = json.load(json_file)
	ports_flag = get_network_ports()
	for data_list_item in data_list:
		dst_ip = data_list_item.keys()[0]
		src_ip_list = data_list_item[dst_ip].keys()
		for src_ip in src_ip_list:
			packet_ids = data_list_item[dst_ip][src_ip].keys()
			packet_ids.reverse()
			count = 1;
			for packet_id in packet_ids:
				packet_data_list = data_list_item[dst_ip][src_ip][packet_id]
				for packet_data_list_item in packet_data_list:
					switch_id = "s{}".format(packet_data_list_item["switch_id"])
					ingress_port = 	int(packet_data_list_item["ingress_port"])
					egress_port = int(packet_data_list_item["egress_port"])
					ports_flag[switch_id][ingress_port] = True
					ports_flag[switch_id][egress_port] = True
				count = count + 1
				if (count > packets_count):
					break


    print "According to {} packets for all the flows following switch ports are working fine".format(packets_count)
    switch_ids = ports_flag.keys()
    #import pdb; pdb.set_trace()
    for switch_id in switch_ids:
     	print "At switch {} following ports are working".format(switch_id)
	ports = ports_flag[switch_id].keys()
	for port in ports:
		if ports_flag[switch_id][port] == True:
			print "	Port: {} inspected and working fine".format(port)
		else:
			print "	Port: {} not inspected".format(port)
	

def execute_options(status):
    if status == 1:
	get_packet_route()

    elif status == 2:
	get_queuing_delay()

    elif status == 3:
	get_queue_depth()

    elif status == 4:
	get_switch_delay()

    elif status == 5:
	get_working_switch_ports()
	
    elif status == 6:
	get_allowed_packet_routes()


def main():
    print "-----------------------------DEBUG TOOL---------------------------\n"
    while True:
	print "\n------------------------------------------------------------------\n"
	print "-> Option1: Inspect Packet Route"
	print "-> Option2: Inspect Queuing delay"
	print "-> Option3: Inspect Queue depth"
	print "-> Option4: Inspect Total delay at a Switch"
	print "-> Option5: Inspect Switches"
	print "-> Option6: Get Allowed Packet Routes according to policy"
	print "-> Option7: Exit"
	status = input("=> Enter your Option")
	if status == 7:
		sys.exit()
	elif status in [1,2,3,4,5,6]:
		execute_options(status)		
		continue
	else:
		print "Wrong input, please try again!"
		continue
	
    
if __name__ == '__main__':
    main()
