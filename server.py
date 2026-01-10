import socket
import time
import struct
import threading

#deck = []
#----------------helper functions----------
def broadcast_offer():
    while True:
        if not is_playing:
            udp_server.sendto(offer_message, ('255.255.255.255', client_offer_msg_port ))
            print("Sent messsage")
            time.sleep(2)

def handle_request(client_socket):
    print("got message ")
    global is_playing
    data = client_socket.recv(38)
    msg = struct.unpack('!IBB32s', data)
    if magic_cookie == msg[0] and request_msg_type == msg[1]:
        num_rounds = msg[2]
        team_raw_name = msg[3]
        team_name = team_raw_name.decode('utf-8').rstrip('\x00')
        print(f"Team {team_name} vs {server_name}!'\n' Let The Game Begin!")
        #handle_game(client_socket, num_rounds)

def handle_game(client_socket, num_round):
    card1 = 1



#--------------------------------------------------------------------  
#----------payload message configuration---------
# magic_cookie
payload_msg_type = 0x4
# round result
# card value
#------------------------------------------------


#----------offer message configuration------
magic_cookie =  0xabcddcba
offer_msg_type = 0x2
server_tcp_port = 0                     #starting value so that the OS gives us an unused port
server_name = "BlackJackinton"
#-------------------------------------------
#-----------------other configurations-----------
client_offer_msg_port = 13122
server_udp_port = 0                     #starting value so that the OS gives us an unused port
server_ip ='0.0.0.0'
is_playing = False
request_msg_type = 0x3
#----------------------------------------------

#-----------creating UDP server---------------
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)    # Enable sending broadcast packets
udp_server.bind(("", server_udp_port))                       # Bind to address
#----------------------------------------------------------------
#----------- creating TCP server---------------
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind(("", server_tcp_port))
tcp_server.settimeout(1.0)
tcp_server.listen()
server_IP, server_tcp_port = tcp_server.getsockname()
print(f"Server started, listening on IP address {server_IP}")
#-----------------------------------------------
#------------------creating encoded offer message-------------
encoded_name = server_name.encode('utf-8')[:32].ljust(32, b'\x00')   # encode the server name and ensure it is 32 bytes long
offer_message = struct.pack('!IBH32s', magic_cookie, offer_msg_type, server_tcp_port, encoded_name)
#-------------------------------------------------------------


threading.Thread(target=broadcast_offer, daemon=True).start() # start UDP thread that sends offers if not in a game

while True:

    try:
        client_socket, client_address = tcp_server.accept()
        #connected to client, stop offers for now
        is_playing = True
        print("got message tcp")

        handle_request(client_socket)
    except socket.timeout:
        continue
    except KeyboardInterrupt:
        print("Closing server")
        tcp_server.close()
        udp_server.close()
        break
    except Exception as e:
        print(f"got an error trying to handle message from client: {e}")
    finally:
        is_playing = False
    #got a message, check if the message is a request msg