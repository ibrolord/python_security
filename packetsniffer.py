import socket, os, struct
from ctypes import *

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

    def __new__(self, socket_buffet=None):
        return self.from_buffer_copy(socket_buffet)

    def __init__(self, socket_buffet=None):

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


host = "172.24.37.39"

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

try:

    while True:

        # read in a single packet
        raw_buffer = sniffer.recvfrom(65535)[0]

        # create an IP header from the first 20 bytes of the buffer
        ip_header = IP(raw_buffer[:20])

        # print protocol detected and the host
        print(f"Protcol: {ip_header.protocol} {ip_header.src} -> {ip_header.dst_address}")

# Ctl-C
except KeyboardInterrupt:
    # turn off promisc mode in windows
    if os.name == "nt": 
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)