import socket
import time
import struct
import threading
import random
from Deck import Deck

# Suit Mapping (for display purposes)
SUITS = {0: "Spades", 1: "Hearts", 2: "Diamonds", 3: "Clubs"}
RANKS = {1: "Ace", 2: "2", 3: "3", 4: "4",5: "5",6: "6",7: "7",8: "8",9: "9",10: "10", 11: "Jack", 12: "Queen", 13: "King"}
#rank to value mapping
RANK_TO_VAL = {1: 11, 2: 2, 3: 3, 4: 4,5: 5,6: 6,7: 7,8: 8,9: 9,10: 10, 11: 10, 12: 10, 13: 10}

#----------------helper functions----------
def get_local_ip():
    """
    This function connects to a public DNS (Google) just to see 
    which network interface the OS decides to use. 
    It doesn't actually send data.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
    
def broadcast_offer():
    while True:
        if not is_playing:
            udp_server.sendto(offer_message, ('255.255.255.255', client_offer_msg_port ))
            #print("Sent messsage")
            time.sleep(2)

def handle_request(client_socket):
    global is_playing
    print("got request ")
    try:
        data = client_socket.recv(38)
        if not data:
            print("Client disconnected before sending data")
            return
        msg = struct.unpack('!IBB32s', data)
        if magic_cookie == msg[0] and request_msg_type == msg[1]:
            num_rounds = msg[2]
            team_raw_name = msg[3]
            team_name = team_raw_name.decode('utf-8').rstrip('\x00')
            print(f"Team {team_name} vs {server_name}!'\n' Let The Game Begin!")
            handle_game(client_socket, num_rounds)
    except OSError as e:
        print(f"client closed the connection: {e}")
    except Exception as e:
        print(f"unexpected error: {e}")
    finally:
        client_socket.close()
        is_playing = False


def handle_game(client_socket, num_round):

    print(num_round)
    for i in range(1 ,num_round+1):
        print(f"Starting round {i}")
        deck = Deck()                   # create a new deck for the round
        p_card1, p_card2, d_card1, d_card2 = initial_deal(client_socket, deck)
        player_score = get_val_by_rank(p_card1) + get_val_by_rank(p_card2)
        dealer_score = get_val_by_rank(d_card1) + get_val_by_rank(d_card2)
        round_status = 0x0
        did_stand = False
        print(f"DEBUG: Starting player score: {player_score}, Starting dealer_score:{dealer_score},player cards: {p_card1} , {p_card2} | dealer cards: {d_card1}, {d_card2}")
        #--------------player turn start-----------------------
        while not did_stand and round_status == 0x0:                      
            print("line 43")              
            cookie, type, decision_raw = struct.unpack('!IB5s',client_socket.recv(10))
            if cookie == magic_cookie and type == payload_msg_type:
                player_decision = decision_raw.decode('utf-8').rstrip('\x00')
                if player_decision == "Hittt" and not did_stand:
                    new_card = drawCard(deck)
                    player_score = player_score + get_val_by_rank(new_card)
                    round_status = check_status(player_score, dealer_score, did_stand)     
                    client_socket.sendall(make_payload(round_status, new_card))
                    # if round_status == 0x2:
                    #     print(f"DEBUG: player score: {player_score}, dealer score: {dealer_score}")
                    #     continue
                    #client_socket.sendall(make_payload(0x0, new_card))
                elif player_decision == "Stand":
                    did_stand =  True
                    # round_status = check_status(player_score, dealer_score, did_stand)
            print(f"DEBUG: player score: {player_score}, dealer score: {dealer_score}")
        #if player busted we go into the if:
        if round_status == 0x2:
            print(f"round ended with result {round_status}, moving on to next round (player busted)")
            continue
        #-----get here only when doing Stand aka not busting----CRUCIAL-----
        second_d_card_msg = make_payload(0x0, d_card2)                                  # dealer turn start
        client_socket.sendall(second_d_card_msg)                                        #reveal second card to player
        #--------------player turn ends-----------------------
        round_status = check_status(player_score, dealer_score, did_stand)  #maybe server is already at score>= 17 and the roudnshould end now
        if round_status != 0x0 :
            # second_d_card_msg = make_payload(0x0, d_card2)                                  # dealer turn start
            # client_socket.sendall(second_d_card_msg)                                                         # check if player lost during his turn
            client_socket.sendall(make_payload(round_status, p_card1))                  #p_card1 here shouldnt be read by the client because round_status is not 0x0
            print(f"round ended with result {round_status}, moving on to next round")
            continue
        #--------------dealer turn starts----------------
        second_d_card_msg = make_payload(0x0, d_card2)                                  # dealer turn start
        client_socket.sendall(second_d_card_msg)                                        #reveal second card to player
        while dealer_score < 17:
            new_d_card = drawCard(deck)
            client_socket.sendall(make_payload(0x0, new_d_card))
            dealer_score = dealer_score + get_val_by_rank(new_d_card)
            time.sleep(1)
        #------------dealer turn ends------------------
        round_status = check_status(player_score, dealer_score, did_stand)
        client_socket.sendall(make_payload(round_status, (0, 0)))
        print(f"Round {i} Result: {round_status}")
    print(f"finished game with player, closing connection")
    client_socket.close()

            
            

#return 0x0 if round is not over, 0x1 if tie, 0x2 if player lost, 0x3 if player won
def check_status(player_score, dealer_score, did_stand):
    if player_score > 21:                       # if player busts, lose immediately
            return 0x2
    elif dealer_score > 21:                     # if dealer busts, win immediately
            return 0x3
    elif dealer_score >= 17 and did_stand:      # if no one busts, but both the player and dealer stopped taking cards
        if player_score > dealer_score:
            return 0x3
        elif dealer_score > player_score:
            return 0x2
        else:
            return 0x1
    else:                                       # if no one busts, but either the player or the dealer keep taking cards
        return 0x0          

    

#assuming card is tuple of <int, int>
def get_val_by_rank(card) :
    result = RANK_TO_VAL.get(card[0])
    if isinstance(result, int) :
        return result
    else:
        raise ValueError("tried to get rank of number not between 1 and 13")

    #returns tuple of 4 cards: 2 of player and 2 of dealer
def initial_deal(client_socket, deck):
    p_card1 = drawCard(deck)
    p_card2 = drawCard(deck)
    d_card1 = drawCard(deck)
    d_card2 = drawCard(deck)
    first_card_msg = make_payload(0x0, p_card1)
    client_socket.sendall(first_card_msg)
    second_card_msg = make_payload(0x0, p_card2)
    client_socket.sendall(second_card_msg)
    first_d_card_msg = make_payload(0x0, d_card1)
    client_socket.sendall(first_d_card_msg)
    return p_card1, p_card2, d_card1, d_card2

def make_payload(round_result : int, card : tuple[int, int] ):
    payload = struct.pack('!IBBHB', magic_cookie, payload_msg_type, round_result, card[0], card[1])
    return payload

#return tuple <rank,suit>
def drawCard(deck):
    card = deck.draw()
    # suit = random.randint(0, 3)
    # rank = random.randint(1, 13)
    return card



#--------------------------------------------------------------------  
#----------payload message configuration---------
# magic_cookie
payload_msg_type = 0x4
# round result
# card rank
#card suit
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
server_ip = get_local_ip()
is_playing = False
request_msg_type = 0x3
#----------------------------------------------

#-----------creating UDP server---------------
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)    # Enable sending broadcast packets
udp_server.bind((server_ip, server_udp_port))                       # Bind to address
#----------------------------------------------------------------
#----------- creating TCP server---------------
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((server_ip, server_tcp_port))
tcp_server.settimeout(1.0)
tcp_server.listen()
_, server_tcp_port = tcp_server.getsockname()

print(f"Server started, listening on IP address {server_ip}")
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