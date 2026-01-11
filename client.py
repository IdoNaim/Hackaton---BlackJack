from scapy.all import *
import socket

# Suit Mapping (for display purposes)
SUITS = {0: "Spades", 1: "Hearts", 2: "Diamonds", 3: "Clubs"}
RANKS = {1: "Ace", 2: "2", 3: "3", 4: "4",5: "5",6: "6",7: "7",8: "8",9: "9",10: "10", 11: "Jack", 12: "Queen", 13: "King"}
#------helper function------
def handle_offer(server_tcp_port, address):
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #create a tcp socket
    tcp_client.connect((address[0], server_tcp_port))
    tcp_client.sendall(request_msg)
    handle_game(tcp_client)

def handle_game(tcp_client):
    wins = 0
    for i in range(1, number_of_rounds+1):
        print(f"-----------------Now starting round {i}---------------")
        time.sleep(2)
        initial_deal(tcp_client)
        playing = True
        while(playing):
            user_decision = input("Whould you like to Hit or Stand? (write only \"Hit\" or \"Stand\")")
            if user_decision == "Hit" :
                user_decision = "Hittt"
                tcp_client.sendall(make_payload(user_decision))
                
                new_card_data = tcp_client.recv(9)
                cookie, type, round_result, card_rank, card_suit = struct.unpack('!IBBHB', new_card_data)
                print(f"Got card: {RANKS.get(card_rank)} of {SUITS.get(card_suit)}")
                if cookie == magic_cookie and type == payload_msg_type and round_result != 0x0:
                    print_result(round_result)
                    playing = False
            elif user_decision == "Stand":
                tcp_client.sendall(make_payload(user_decision))
                print("Standing, waiting for dealer")
                second_d_card = struct.unpack('!IBBHB', tcp_client.recv(9)) #should be getting the second card of the dealer revealed
                print(second_d_card)
                if second_d_card[0] != magic_cookie or second_d_card[1] != payload_msg_type or second_d_card[2] != 0x0:
                    raise Exception("got error when revealing second dealer card")
                print(f"The dealer's second card is {RANKS.get(second_d_card[3])} of {SUITS.get(second_d_card[4])}")

                while True:                                             # from now on the dealer should be hitting
                    new_card_data = tcp_client.recv(9)
                    if not new_card_data: break
                    
                    cookie, type, round_result, card_rank, card_suit = struct.unpack('!IBBHB', new_card_data)
                    
                    if round_result != 0x0:
                        if round_result == 0x3:
                            wins = wins+1
                        print_result(round_result)
                        playing = False # Exit outer loop
                        break 
                    
                    # If result is 0, it's a dealer card being revealed
                    print(f"Dealer drew: {RANKS.get(card_rank, card_rank)} of {SUITS.get(card_suit, card_suit)}")
            else:
                print("please write only hit or stand! don't make me angry >:(")
                continue
    print(f"Finished playing {number_of_rounds} rounds, win rate: {wins/number_of_rounds}")
    tcp_client.close()
    
def print_result(res):
    if res == 0x1: print("It's a Draw!")
    elif res == 0x2: print("You Lost!")
    elif res == 0x3: print("You Won!")

def initial_deal(tcp_client):
    data = tcp_client.recv(9)
    server_payload = struct.unpack('!IBBHB', data)
    print(f"Your first card: {RANKS.get(server_payload[3])} of {SUITS.get(server_payload[4])}")
    data = tcp_client.recv(9)
    server_payload = struct.unpack('!IBBHB', data)
    print(f"Your second card: {RANKS.get(server_payload[3])} of {SUITS.get(server_payload[4])}")
    data = tcp_client.recv(9)
    server_payload = struct.unpack('!IBBHB', data)
    print(f"the dealers first card: {RANKS.get(server_payload[3])} of {SUITS.get(server_payload[4])}")

def make_payload(player_decision_str):
    endoced_decision = player_decision_str.encode('utf-8')[:5].ljust(5, b'\x00')
    payload = struct.pack('!IB5s',magic_cookie, payload_msg_type, endoced_decision)
    return payload

def input_num_of_rounds():
    global number_of_rounds
    try:
        rounds_str = input("How many round would you like to play?\n")
        rounds_int = int(rounds_str)
        if 1 <= rounds_int and rounds_int <=255 :
            number_of_rounds = rounds_int 
        else:
            print("illegal number of rounds, can only do between 1 and 255, setting round to 1")
    except ValueError:
        print("not a number! setting rounds to 1")
    except EOFError:
        print("Closing client")
        udp_client.close()
        exit()
    except Exception:
        print("got an error")
        udp_client.close()
        exit()

def create_request_message():
    global request_msg
    request_msg = struct.pack('!IBB32s', magic_cookie, request_msg_type, number_of_rounds, encoded_name)
#--------------------------------------
#-----------payload message format----------------
#magic_cookie
payload_msg_type = 0x4
#player_decision 
#-------------------------------------------------
#------------requst message format------------
magic_cookie = 0xabcddcba
request_msg_type = 0x3
number_of_rounds = 1
team_name = "DaWinnersXDXD"
#---------------------------
#------------UDP configurations----------
offer_msg_port = 13122
offer_msg_type = 0x2
udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to "0.0.0.0" (all interfaces) and the specific port
udp_client.bind(("", offer_msg_port))
udp_client.settimeout(1.0)

#----------------------------------------
#----------forming request message----------
encoded_name = team_name.encode('utf-8')[:32].ljust(32, b'\x00')   # encode the server name and ensure it is 32 bytes long
request_msg = struct.pack('!IBB32s', magic_cookie, request_msg_type, number_of_rounds, encoded_name)
#--------------------------------------------




while True:
    print(f"Started Client, listening for offer requests on IP address {udp_client.getsockname()}")
    input_num_of_rounds()
    create_request_message()
    try:
        data, addr = udp_client.recvfrom(39)
        msg = struct.unpack('!IBH32s', data)
        cookie = msg[0]             
        msg_type = msg[1]
        server_tcp_port = msg[2]
        raw_name = msg[3]
        server_name = raw_name.decode('utf-8').rstrip('\x00')      #name as string
        if cookie == magic_cookie and msg_type == offer_msg_type:
            print(f"recieved offer from {server_name} on IP {addr[0]}")
            handle_offer(server_tcp_port, addr)
    except socket.timeout:
        continue
    except KeyboardInterrupt:
        print("Closing client")
        udp_client.close()
        break