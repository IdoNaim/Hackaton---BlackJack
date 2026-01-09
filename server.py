import socket
import time
import struct

# offer message configuration
magic_cookie =  0xabcddcba
offer_msg_type = 0x2
server_tcp_port = 5000
server_name = "BlackJackinton"
#-----------------------------
#other configurations
client_offer_msg_port = 13122
server_udp_port = 0
server_ip ='0.0.0.0'


# creating UDP server
# 1. Create a UDP socket (SOCK_DGRAM = UDP)
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Enable sending broadcast packets
udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# 2. Bind to address
udp_server.bind(server_ip, server_udp_port)
#----------------------------------------------------------------

#creating encoded offer message to send
encoded_name = server_name.encode('utf-8')[:32].ljust(32, b'\x00')   # encode the server name and ensure it is 32 bytes long
offer_message = struct.pack('!IBH32s', magic_cookie, offer_msg_type, server_tcp_port, encoded_name)
print("UDP Server is waiting for packets...")

while True:
    # # 3. Receive data and the address it came from
    # data, addr = udp_server.recvfrom(1024)
    # print(f"Received {data.decode('utf-8')} from {addr}")
    
    # 4. Reply (optional)
    udp_server.sendto(b"Sigma macho", ('255.255.255.255',offer_msg_port ))
    print("Sent messsage")
    time.sleep(2)