import socket
import random
from mysocket import *

# Generate gameboard
def gen_board():
    board = [[[0] * 5 for i in range(5)] for j in range(5)]
    for player in range(5):
        arr = random.sample(range(1, 100), 25)
        for i in range(5):
            for j in range(5):
                board[player][i][j] = arr[i * 5 + j]
    return board

# Convert board to string (for transfer)
def board2str(board):
    ret = ''
    for i in range(5):
        for j in range(5):
            ret += str(board[i][j]) + ' '
    return ret.strip()

# Calculate greedy score for each position
def calcpt(board, i, j):
    ret = 0

    # Row
    r = True
    pt = 1
    for a in range(5):
        if board[i][a] < 0:
            pt *= 5
    ret += pt

    # Column
    r = True
    pt = 1
    for a in range(5):
        if board[a][j] < 0:
            pt *= 5
    ret += pt

    # Diagonal 1
    if i == j:
        r = True
        pt = 1
        for a in range(5):
            if board[a][a] < 0:
                pt *= 5
        ret += pt
    
    # Diagonal 2
    if i == 4-j:
        r = True
        pt = 1
        for a in range(5):
            if board[a][4-a] < 0:
                pt *= 5
        ret += pt

    return ret

# Greedy select for AI player
def selectnum(board):
    sel = board[0][0]
    mx = 0
    for i in range(5):
        for j in range(5):
            pt = calcpt(board, i, j)
            if mx < pt:
                mx = pt
                sel = board[i][j]
    return sel

# Process gameboard with selected number num
def process(gameboard, num):
    for p in range(5):
        for i in range(5):
            for j in range(5):
                if gameboard[p][i][j] == num:
                    gameboard[p][i][j] = -num
    return gameboard

# Check if gane finished
def chkend(board):
    # Row
    r = True
    for i in range(5):
        r = True
        for j in range(5):
            if board[i][j] > 0:
                r = False
                break
        if r:
            return True
    
    # Column
    for i in range(5):
        r = True
        for j in range(5):
            if board[j][i] > 0:
                r = False
                break
        if r:
            return True

    # Diagonal
    r = True
    for i in range(5):
        if board[i][i] > 0:
            r = False
            break
    if r:
        return True

    r = True
    for i in range(5):
        if board[i][4-i] > 0:
            r = False
            break
    if r:
        return True

    return False

# Check if copartner plays in right way
def cheatCheck(board, cheat, sel):
    if cheat == 0:
        return True
    f = False
    for i in range(5):
        for j in range(5):
            if board[i][j] == cheat:
                f = True
                break
        if f:
            break
    if not f:
        return True
    return cheat == sel

def run_server(sock):
    return
    # Current number of players. Start from 3 due to AI players.
    player_count = 3

    # Connections for 2 clients.
    conn = [0, 0]
    addr = [0, 0]
    gameboard = gen_board()
    userid = [None, None]  # login status

    # Role assignment   0: Main_culprit, 1: Copartner
    role = random.sample(range(2), 2)   # 1st arrival: role[0], 2nd arrival: role[1]
    role += [2, 2, 2]

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

    # Game Ready, send gameboard to clients
    for i in range(2):
        send_to(conn[i], 'S', board2str(gameboard[i]))

    # Constant
    culprit = 0
    copartner = 1

    # Game Loop
    cnt = 0
    winner = None
    cheat = 0  # Cheating number from main_culprit to copartner

    while True: 
        player = turn[cnt]
        sel = 0

        # Client
        if role[player] == culprit:
            send_to(conn[player], 'T', board2str(gameboard[player]))
            read = read_from(conn[player])["data"]
            sel = int(read[0])
            cheat = int(read[1])

        elif role[player] == copartner:
            send_to(conn[player], 'T ' + str(cheat), board2str(gameboard[player]))
            while True:
                read = read_from(conn[player])["data"]
                sel = int(read[0])
                if cheatCheck(gameboard[player], cheat, sel):
                    break
                else:   # Wrong behavior, Reject
                    send_to(conn[player], 'R')

        else:
            sel = selectnum(gameboard[player])
        
        # Update gameboard
        gameboard = process(gameboard, sel)
        for p in range(5):
            send_to(conn[p], 'U', board2str(gameboard[p]))

        # Game finish check
        if chkend(gameboard[player]):
            winner = player
            break

        cnt += 1
    
    print('Game Finished')
    if winner <= 1:
        print('Winner: ' + userid[winner])
    else:
        print('Winner: AI_' + str(winner-2))
    
    
    
    ##### mylst = list(map(int, ndata.split(' ')))

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
    # Game Start:   'S 00 00 00 ... 00' => 25 number with S prefix, R role (0 for main culprit, 1 for copartner)
    # Update board: 'B 00 00 00 ... 00' => 25 number with U prefix
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
    

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 20395

    # Create Server Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    
    run_server(s)
    
    s.close()