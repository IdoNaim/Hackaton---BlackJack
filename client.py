from scapy.all import *
import socket

offer_msg_port = 13122

udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to "0.0.0.0" (all interfaces) and the specific port
udp_client.bind(("0.0.0.0", offer_msg_port))
while True:
    data, addr =udp_client.recvfrom(39)
    print(f"{data.decode('utf-8')}")




#udp_client.close()