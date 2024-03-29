import socket
import random
import time
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
    if board[i][j] < 0:
        return -1
    ret = 0

    # Row
    pt = 1
    for a in range(5):
        if board[i][a] < 0:
            pt *= 5
    ret += pt

    # Column
    pt = 1
    for a in range(5):
        if board[a][j] < 0:
            pt *= 5
    ret += pt

    # Diagonal 1
    if i == j:
        pt = 1
        for a in range(5):
            if board[a][a] < 0:
                pt *= 5
        ret += pt
    
    # Diagonal 2
    if i == 4-j:
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
def chkendplayer(board):
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

def chkend(gameboard):
    winner = []
    for p in range(5):
        if chkendplayer(gameboard[p]):
            winner.append(p)
    return winner

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
    # clientections for 2 clients.
    client = [0, 0]
    addr = [0, 0]
    gameboard = gen_board()
    userid = [None, None]  # login status
    userid += ['AI_0', 'AI_1', 'AI_2']

    # Role assignment   0: Main_culprit, 1: Copartner
    role = random.sample(range(2), 2)   # 1st arrival: role[0], 2nd arrival: role[1]
    role += [2, 2, 2]

    # Decide turn[0]
    turn = random.sample(range(5), 5)

    print('Server running...')

    # Login Phase
    nc = 0
    while nc < 2:
        client[nc], addr[nc] = sock.accept()
        print('Accept from ' + str(addr[nc]))

        read = read_from(client[nc])["data"][0]
        print('Requested ID: ' + read)

        if nc == 1 and userid[0] == read:
            print('Duplicate ID exists. Reject')
            send_to(client[nc], 'F')
            continue
        print('Accepted')
        userid[nc] = read
        send_to(client[nc], 'P', str(role[nc]))
        nc += 1

    # Game Ready, send gameboard to clients
    for i in range(2):
        send_to(client[i], 'S', board2str(gameboard[i]))
    
    print('Game Start!!')
    print('Turn: ' + str(turn))
    # Constant
    culprit = 0
    copartner = 1

    cnt = 0
    winner = []
    cheat = 0   # Cheating number from main_culprit to copartner

    # Game Loop
    while True:
        time.sleep(0.5)
        player = turn[cnt]
        sel = 0
        print('Player ' + str(player) + "'s turn")
        print('Cheat Number: ' + str(cheat))

        # Client
        if role[player] == culprit:
            send_to(client[player], 'T', board2str(gameboard[player]))
            # Read number
            read = read_from(client[player])["data"]
            sel = int(read[0])

            # Process with selected number
            gameboard = process(gameboard, sel)

            # Game finish check
            winner = chkend(gameboard)
            if winner:
                break
            
            for p in range(2):
                send_to(client[p], 'U', board2str(gameboard[p]))

            # Read cheat number
            read = read_from(client[player])["data"]
            cheat = int(read[0])

        elif role[player] == copartner:
            # Send cheat with turn start signal 'T'
            send_to(client[player], 'T ' + str(cheat), board2str(gameboard[player]))
            while True:
                read = read_from(client[player])["data"]
                sel = int(read[0])
                if cheatCheck(gameboard[player], cheat, sel):
                    break
                else:   # Wrong behavior, Reject
                    send_to(client[player], 'R')

        else:
            sel = selectnum(gameboard[player])
        
        print('Player ' + str(player) + ' selected ' + str(sel))
        # Update gameboard
        gameboard = process(gameboard, sel)
        for p in range(2):
            send_to(client[p], 'U', board2str(gameboard[p]))

        # Game finish check
        winner = chkend(gameboard)
        if winner:
            break

        cnt += 1
        cnt %= 5
    # end Game Loop

    # Finished
    print('Game Finished')
    winnerstring = ''
    winnerid = list(map(lambda x:userid[x], winner))
    for w in winnerid:
        print('Winner: ' + w)
        winnerstring += w + ' '
    for i in range(2):
        send_to(client[i], 'W', winnerstring)



if __name__ == "__main__":
    # Connection Information
    HOST = '127.0.0.1'
    PORT = 20395

    # Create Server Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    
    run_server(s)
    
    s.close()