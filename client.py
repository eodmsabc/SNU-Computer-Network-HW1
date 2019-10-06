import socket
from mysocket import *

def parse_board(ins):
    return [[int(ins[i * 5 + j]) for j in range(5)] for i in range(5)]

def printboard(board):
    for i in range(5):
        print(board[i])

def run_client(HOST, PORT):
    server = None
    role = None
    board = None
    culprit = 0
    copartner = 1
    
    # Login Phase
    while True:
        userid = input('Enter User ID: ')
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((HOST, PORT))

        send_to(server, 'U', userid)
        read = read_from(server)
        
        if read["type"] == 'P':
            role = int(read["data"][0])
            print('User ID: ' + userid + ', Role: ' + ('Culprit' if role == 0 else 'Copartner'))
            break
        else:
            print('Duplicate ID exists. Rejected from server.')
            server.close()
            continue
    
    # Game Ready
    print('Waiting...')
    read = read_from(server)
    if read["type"] != 'S':
        print('Signal Error: Received ' + read["type"] + ', Expected S')
        server.close()
        return
    board = parse_board(read["data"])

    # Game Start
    print('Game Start with following board')
    print(board)
    winner = []

    # Game Loop
    while True:
        read = read_from(server)
        header = read["type"]
        data = read["data"]

        if header == 'W':
            winner = read["data"]
            break
        elif header == 'U':
            board = parse_board(data)
        elif header == 'T':
            print('Your Turn!')
            printboard(board)
            if role == culprit:
                board = parse_board(data)
                sel = input("Select Number: ")
                cheat = input("Select Cheat: ")
                send_to(server, 'N', sel + ' ' + cheat)
            else:
                cheat = data[0]
                board = parse_board(data[1:])
                print('Cheat number: ' + cheat)
                sel = input("Select Number: ")
                send_to(server, 'N', sel)
        
        #Rejected
        elif header == 'R':
            print('Wrong behavior!!! Rejected from server')
            print('Cheat number: ' + cheat)
            sel = input("Select Number: ")
            send_to(server, 'N', sel)

        else:
            print('Server Disconnected')
            break


    print('Game Finished')
    for w in winner:
        print('Winner: ' + w)
    # Close
    server.close()


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 20395
    run_client(HOST, PORT)