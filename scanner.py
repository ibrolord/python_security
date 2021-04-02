import socket, os, struct, threading, time
from netaddr import IPNetwork,IPAddress
from ctypes import *

host = "172.24.37.39"

subnet = "255.255.255.0/24"

## needs fix
# ICMP Header
class ICMP(Structure):
    _fields_ = [

        ("type",         c_ubyte),
        ("code",         c_ubyte),
        ("checksum",     c_ushort),
        ("unused",       c_ushort),
        ("next_hop_mtu", c_ushort)
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass

# IP Header
class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint32),
        ("dst", c_uint32)
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        # map protocol consts to their names
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}

        # human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("<L",self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L",self.dst))

        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

magic_message = "PYTHONRULESS!"

def udp_sender(subnet,magic_message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message,("%s" % ip,65212))
        except:
            pass


# raw socket
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP

else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# IP Headers included in capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# Send IOCTL for windows for promisc mode
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# start sending packets
t = threading.Thread(target=udp_sender,args=(subnet,magic_message))
t.start()


try:

    while True:

        # read in a single packet
        raw_buffer = sniffer.recvfrom(65535)[0]

        # create an IP header from the first 20 bytes of the buffer
        ip_header = IP(raw_buffer[:20])

        # print protocol detected and the host
        print(f"Protcol: {ip_header.protocol} {ip_header.src} -> {ip_header.dst_address}")

        # check for the TYPE 3 and CODE
        if icmp_header.code == 3 and icmp_header.type == 3:

            # make sure host is our target subnet
            if IPAddress(ip_header.src_address) in IPNetwork(subnet):

                if raw_buffer[len(raw_buffer)-len(magic_message):] == magic_message:
                    print(f"Host Up: {ip_header.src_address}")
       
        # if it's ICMP
        if ip_header.protocol == "ICMP":

            # calculate where ICMP packet starts
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]

            # create ICMP structure
            icmp_header = ICMP(buf)

            print(f"ICMP -> Type: {icmp_header.type} Code: {icmp_header.type, icmp_header.code})

# Ctl-C
except KeyboardInterrupt:
    # turn off promisc mode in windows
    if os.name == "nt": 
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)