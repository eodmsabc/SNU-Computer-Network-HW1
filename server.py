import socket
import random
from mysocket import *

def gen_board():
    return 0

def run_server(sock):
    # Current number of players. Start from 3 due to AI players.
    player_count = 3

    # Connections for 2 clients.
    conn = [0, 0]
    addr = [0, 0]
    gameboard = gen_board()
    userid = [None, None]  # login status

    # Role assignment   0: Main_culprit, 1: Copartner
    role = random.sample(range(2), 2)   # 1st arrival: role[0], 2nd arrival: role[1]

    # Decide turn[0]
    turn = random.sample(range(5), 5)

    print('Server running...')

    # Login Phase
    nc = 0
    while nc < 2:
        conn[nc], addr[nc] = sock.accept()
        print('Accept from ' + str(addr[nc]))

        read = read_from(conn[nc])["data"][0]
        print(read)
        print('Requested ID: ' + read)

        if nc == 1 and userid[0] == read:
            send_to(conn[nc], 'F')
            continue

        userid[nc] = read
        send_to(conn[nc], 'P', str(role[nc]))
        nc += 1

    # Game Start
    send_to(conn[0], 'S')
    send_to(conn[1], 'S')
        # mylst = list(map(int, ndata.split(' ')))

    # when 2 human players are connected, server sends to these players 'game start' signal with initial game board.
    # client state changes from wait to game

    # Game progress
    # i; 0>1>2>3>4>0>1>2>...
    # turn[i] = k, kth player playes
    # if k == 0 or 1 then server let player know that it's now player's turn (send to conn[k])
    # if role[k] == 0 then conn[k] is main_culprit, wait for 2 number, first one is bingo num, second is cheat
    # else if role[k] == 1 then conn[k] is copartner. server sends cheat number with start signal.
    # server checks if copartner plays correct way. if good, send 'turn end' signal. if not, replay signal.
    # if k is main_culprit, after receiving cheat num, server send ack (turn end) right after applying bingo result.
    # after applying bingo result, server sends to all players with updated bingo game board.
    # if bingo game ends, server sends 'turn end' signal to last player and send 'game finish' signal to all connected player (0, 1) instead of updated bingo board.
    # with winner information.

    # if the game is not end yet, i increases and next turn starts

    # protocol
    # Game Start:   'S R 00 00 00 ... 00' => 25 number with S prefix, R role (0 for main culprit, 1 for copartner)
    # Update board: 'U 00 00 00 ... 00' => 25 number with U prefix
    # Start turn:   'T'
    # Client ans:   '00'
    # Finish:       'F W' => W is winner (0 ~ 4) 0 is main culprit, 1 is copartner, 2~4: AI player.
    # Client compare W with own role. if match, you win! else if partner, ... else ai_n wins

    #if True:
        # Waiting Players
        #while num_player < 5:
            #conn[num_player - 3], addr[num_player - 3] = s.accept()
            #print('Connected by ', addr[num_player - 3])
            #num_player += 1
        
    #    print("5 players ready. Game Start.")
        # Game Start
    #    while True:
    #        con, add = s.accept()
     #       data = con.recv(1024)
            #if not data:
             #   break
     #       con.sendall(data)
    
    #s.close()

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 20395

    # Create Server Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    
    run_server(s)
    
    s.close()