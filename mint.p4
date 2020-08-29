/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>


#define MAX_STACK_LENGTH 3
#define MAX_HOP_COUNT 4

const bit<16> TYPE_IPV4      = 0x800;
const bit<16> TYPE_MPLS	     = 0x8847;	
const bit<8>  PROTOCOL_TCP   = 0x06;
const bit<8>  PROTOCOL_UDP   = 0x11;
const bit<8>  PROTOCOL_MINT  = 0xFD;		/* Experimetal value*/
const bit<4>  GNS	     = 0x1;
const bit<8>  REQUEST_VECTOR = 0x1F;


/*
GNS ID = 1 specifies following metadata
Request_Vector_Bit[0] - deque time delta
Request_Vector_Bit[1] - enqueue depth
Request_Vector_Bit[2] - total delay at switch
Request_Vector_Bit[3] - ingress port
Request_Vector_Bit[4] - egress port
Request_Vector_Bit[5] - enque timestamp
Request_Vector_Bit[6] - dequeue qdepth
*/


/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;


header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header mpls_t {
    bit<20> label_id;
    bit<3>  tc;
    bit     bos;
    bit<8>  ttl;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header mint_hdr_t {
    bit<4>    version;
    bit<4>    gns;
    bit<8>    next_header;
    bit<8>    flags;
    bit<8>    max_len;	 
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<8>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}

header mint_metadata_hdr_t {
    bit<8> action_vector;
    bit<8> request_vector;
    bit<8> hop_limit;
    bit<8> current_length;
}

header mint_metadata_t {
   bit	   bos;
   bit<31> switch_id;
   bit<32> deq_timedelta;
   bit<32> enq_qdepth;
   bit<48> delay_at_switch;
   bit<12>  ingress_port;
   bit<12>  egress_port;
}

struct metadata {
   bit<8> status;
}

struct headers {
    ethernet_t   	   	 	ethernet;
    mpls_t[MAX_STACK_LENGTH] 		mpls;
    ipv4_t       	    		ipv4;
    mint_hdr_t				mint_hdr;
    tcp_t				tcp;
    udp_t				udp;
    mint_metadata_hdr_t			mint_metadata_hdr;
    mint_metadata_t[MAX_HOP_COUNT-1]	mint_metadata;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
	packet.extract(hdr.ethernet);
    	transition select(hdr.ethernet.etherType) {
	   TYPE_IPV4 : parse_ipv4;
           TYPE_MPLS : parse_mpls;
	   default : accept;
        }
    }

    state parse_mpls {
         packet.extract(hdr.mpls.next);
         transition select(hdr.mpls.last.bos) {
            0 : parse_mpls; 
            1 : parse_ipv4;
         }
    }

    state parse_ipv4 {
    	packet.extract(hdr.ipv4);
	transition select(hdr.ipv4.protocol) {
	   PROTOCOL_TCP  : parse_tcp;
	   PROTOCOL_UDP  : parse_udp;
	   PROTOCOL_MINT : parse_mint_hdr;
	   default : accept;   	
	}
    }

    state parse_mint_hdr {
    	packet.extract(hdr.mint_hdr);
	transition select(hdr.mint_hdr.next_header) {
	   PROTOCOL_TCP	: parse_tcp;
	   PROTOCOL_UDP : parse_udp;
	   default : accept;	
	}
    }

    state parse_tcp {
    	packet.extract(hdr.tcp);
	transition select(hdr.mpls[1].isValid()) {
	   true : parse_mint_metadata_hdr;
	   default : accept;	
        }
    }

    state parse_udp {
    	packet.extract(hdr.udp);
	transition select(hdr.mpls[1].isValid()) {
	   true : parse_mint_metadata_hdr;
	   default : accept;	
        }
    }

    state parse_mint_metadata_hdr {
    	packet.extract(hdr.mint_metadata_hdr);
	hdr.mint_metadata_hdr.hop_limit = hdr.mint_metadata_hdr.hop_limit - 1;
	transition select(hdr.mint_metadata_hdr.hop_limit) {
	   0 : accept;
	   default : parse_metadata;	
	}
    }

    state parse_metadata {
    	packet.extract(hdr.mint_metadata.next);
         transition select(hdr.mint_metadata.last.bos) {
            1 : accept; 
            0 : parse_metadata;
         }
    }	    
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
   
    action tunnel_forward(egressSpec_t port) {
    	standard_metadata.egress_spec = port;
    }

    action drop() {
    	mark_to_drop(standard_metadata);
    }

    action enable_mint(bit<8> status_bit) {
    	meta.status = status_bit;
    }

    action set_label(bit<20> label) {
    	hdr.mpls[0].label_id = label;
    }

    table label_match {
    	key = {
	   hdr.mpls[0].label_id: exact;	
	}
	actions = {
	   tunnel_forward;
	   drop;	
	}
	size = 30;
        default_action = drop();
    }

    table attach_label {
    	key = {
           hdr.ipv4.dstAddr: lpm;
        }
	actions = {
	   set_label;
	   drop;	
	}
	size = 30;
        default_action = drop();
    }

    table mint_status {
    	actions = {
	    enable_mint;
	    NoAction;	
	}
	default_action = NoAction();
    }
    
    apply {

	mint_status.apply();
	
	if(hdr.ethernet.etherType == TYPE_IPV4) {
		hdr.ethernet.etherType = TYPE_MPLS;
		hdr.mpls[0].setValid();
		hdr.mpls[0].bos = (bit<1>) 1;
		hdr.mpls[0].tc = (bit<3>) 0;
		hdr.mpls[0].ttl = (bit<8>) 255;
		attach_label.apply();	
	}

	if(meta.status == (bit<8>)1 && hdr.mpls[1].isValid() == false) {
		hdr.mpls[0].bos = (bit<1>) 0;
		hdr.mpls[1].setValid();
		hdr.mpls[1].label_id = (bit<20>) 15;
		hdr.mpls[1].tc = (bit<3>) 0;
		hdr.mpls[1].bos = (bit<1>) 0;
		hdr.mpls[1].ttl = (bit<8>) 255;
		hdr.mpls[2].setValid();
		hdr.mpls[2].label_id = (bit<20>) 16;
		hdr.mpls[2].tc = (bit<3>) 0;
		hdr.mpls[2].bos = (bit<1>) 1;
		hdr.mpls[2].ttl = (bit<8>) 255;		
		hdr.mint_hdr.setValid();
		hdr.mint_hdr.version = (bit<4>) 2;
		hdr.mint_hdr.gns = (bit<4>) GNS;
		hdr.mint_hdr.next_header = (bit<8>) hdr.ipv4.protocol;
		hdr.ipv4.protocol = PROTOCOL_MINT;
		hdr.mint_hdr.flags = (bit<8>) 0x04;
		hdr.mint_hdr.max_len = (bit<8>) 0;
		hdr.mint_metadata_hdr.setValid();
		hdr.mint_metadata_hdr.action_vector = (bit<8>) 0;
		hdr.mint_metadata_hdr.request_vector = (bit<8>) REQUEST_VECTOR;
		hdr.mint_metadata_hdr.hop_limit = (bit<8>) MAX_HOP_COUNT-1;
		hdr.mint_metadata_hdr.current_length = (bit<8>) 0;
		hdr.mint_metadata[0].setValid();
		hdr.mint_metadata[0].bos = (bit<1>) 1;
		hdr.mint_metadata[0].switch_id = (bit<31>) 0;
		hdr.mint_metadata[0].deq_timedelta = (bit<32>) 0;
		hdr.mint_metadata[0].enq_qdepth = (bit<32>) 0;
		hdr.mint_metadata[0].delay_at_switch = (bit<48>) 0;
		hdr.mint_metadata[0].ingress_port = (bit<12>) 0;
		hdr.mint_metadata[0].egress_port = (bit<12>) 0;
	}

	label_match.apply();
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    action set_switch_id(bit<31> switch_id) {
        hdr.mint_metadata[0].switch_id = (bit<31>)switch_id;
    }

    table switch_id {
        actions = {
            set_switch_id;
            NoAction;
        }
        default_action = NoAction();
    }
    
    apply {  
    	if (hdr.mpls[2].isValid()) {
	    if(hdr.mint_metadata_hdr.hop_limit != MAX_HOP_COUNT-1) {
		hdr.mint_metadata.push_front(1);
	    }
	    hdr.mint_metadata[0].setValid();
	    switch_id.apply();
	    if(hdr.mint_metadata_hdr.hop_limit != MAX_HOP_COUNT-1) {
		hdr.mint_metadata[0].bos = 0;
            }
	    else {
	        hdr.mint_metadata[0].bos = 1;
            }
	    if (hdr.mint_metadata_hdr.request_vector == REQUEST_VECTOR) {
	    	hdr.mint_metadata[0].deq_timedelta = (bit<32>)standard_metadata.deq_timedelta;  
	    	hdr.mint_metadata[0].enq_qdepth    = (bit<32>)standard_metadata.enq_qdepth;  
	    	hdr.mint_metadata[0].delay_at_switch = (bit<48>)(standard_metadata.egress_global_timestamp -  		standard_metadata.ingress_global_timestamp);
	    	hdr.mint_metadata[0].ingress_port = (bit<12>) standard_metadata.ingress_port;
	    	hdr.mint_metadata[0].egress_port = (bit<12>) standard_metadata.egress_port;
	    	hdr.ipv4.totalLen = hdr.ipv4.totalLen + 29;
		hdr.mint_metadata_hdr.current_length = hdr.mint_metadata_hdr.current_length + 21; 
            }
	}
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
	packet.emit(hdr.mpls);	
	packet.emit(hdr.ipv4);
        packet.emit(hdr.mint_hdr);
	packet.emit(hdr.tcp);
	packet.emit(hdr.udp);
	packet.emit(hdr.mint_metadata_hdr);
	packet.emit(hdr.mint_metadata);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
