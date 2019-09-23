import socket
import random

def run_server():
    HOST = '127.0.0.1'
    PORT = 20395
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)

    num_player = 3
    #conn = [0, 0]
    #addr = [0, 0]
    role = random.sample(range(2), 2) # 0: Main_culprit, 1: Copartner
    turn = random.sample(range(5), 5)
    print(str(role))

    if True:
        # Waiting Players
        #while num_player < 5:
            #conn[num_player - 3], addr[num_player - 3] = s.accept()
            #print('Connected by ', addr[num_player - 3])
            #num_player += 1
        
        print("5 players ready. Game Start.")
        # Game Start
        while True:
            con, add = s.accept()
            data = con.recv(1024)
            #if not data:
             #   break
            con.sendall(data)

if __name__ == "__main__":
    run_server()