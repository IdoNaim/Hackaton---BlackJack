from scapy.all import *
import socket


#------helper function------
def handle_offer(server_tcp_port, server_name, address):
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #create a tcp socket
    tcp_client.connect((address[0], server_tcp_port))
    tcp_client.sendall(request_msg)
    #tcp_client.sendto(request_msg, (address[0], server_tcp_port))
#--------------------------------------
#------------requst message format------------
magic_cookie = 0xabcddcba
request_msg_type = 0x3
number_of_rounds = 1
team_name = "DaWinnersXDXD"
#---------------------------
#------------udp configurations----------
offer_msg_port = 13122
offer_msg_type = 0x2
udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to "0.0.0.0" (all interfaces) and the specific port
udp_client.bind(("0.0.0.0", offer_msg_port))
udp_client.settimeout(1.0)
#----------------------------------------
#----------forming request message----------
encoded_name = team_name.encode('utf-8')[:32].ljust(32, b'\x00')   # encode the server name and ensure it is 32 bytes long
request_msg = struct.pack('!IBB32s', magic_cookie, request_msg_type, number_of_rounds, encoded_name)
#--------------------------------------------




while True:
    try:
        data, addr = udp_client.recvfrom(39)
        msg = struct.unpack('!IBH32s', data)
        cookie = msg[0]             
        msg_type = msg[1]
        server_tcp_port = msg[2]
        raw_name = msg[3]
        server_name = raw_name.decode('utf-8').rstrip('\x00')      #name as string
        if cookie == magic_cookie and msg_type == offer_msg_type:
            handle_offer(server_tcp_port, server_name, addr)
    except socket.timeout:
        continue
    except KeyboardInterrupt:
        print("Closing client")
        udp_client.close()
        break