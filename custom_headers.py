from scapy.all import *

TYPE_MPLS 	=  0x8847
PROTOCOL_TCP 	=  0x06
PROTOCOL_UDP    =  0x11
PROTOCOL_MINT   =  0xFD
GNS             =  1

class mpls(Packet):
   name="mpls"
   fields_desc = [ BitField("label_id", 0, 20),
		   BitField("tc", 0, 3),
                   BitField("bos", 0, 1),
		   BitField("ttl", 0, 8)
		 ]


class mint_hdr(Packet):
   name="mint_hdr"
   fields_desc = [ BitField("version", 2, 4),
		   BitField("gns", 0, 4),
                   BitField("next_header", 0, 8),
		   BitField("flags", 0, 8),
		   BitField("max_len", 0, 8)
		 ]

class mint_metadata_hdr(Packet):
   name="mint_metadata_hdr"
   fields_desc = [ BitField("action_vector", 0, 8),
		   BitField("request_vector", 0, 8),
                   BitField("hop_limit", 4 , 8),
		   BitField("current_length", 0, 8)
		 ]

class mint_metadata(Packet):
   name="mint_metadata"
   fields_desc = [ 
		   BitField("bos", 1 , 1),
		   BitField("switch_id", 0, 31),
		   BitField("deq_timedelta", 0, 32),
		   BitField("enq_qdepth", 0 , 32),
		   BitField("delay_at_switch",0,48),
		   BitField("ingress_port",0,12),
		   BitField("egress_port",0,12)
		 ]

bind_layers(Ether, mpls, type=TYPE_MPLS)
bind_layers(mpls, mpls, bos=0)
bind_layers(mpls, IP, bos=1)
bind_layers(IP, mint_hdr, proto=PROTOCOL_MINT)
bind_layers(IP, TCP, proto=PROTOCOL_TCP)
bind_layers(IP, UDP, proto=PROTOCOL_UDP)
bind_layers(mint_hdr, TCP, next_header=PROTOCOL_TCP)
bind_layers(mint_hdr, UDP, next_header=PROTOCOL_UDP)
#bind_layers(TCP, mint_metadata_hdr)
#bind_layers(UDP, mint_metadata_hdr)
#bind_layers(mint_metadata_hdr, mint_metadata)
#bind_layers(mint_metadata, mint_metadata, bos=0)
#bind_layers(mint_metadata, Raw, bos=1)
