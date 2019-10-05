import socket
from mysocket import *

def run_client(HOST, PORT):
    sock = None
    role = None
    # Login Phase
    while True:
        userid = input()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))

        send_to(sock, 'U', userid)
        read = read_from(sock)
        
        if read["type"] == 'P':
            role = int(read["data"][0])
            print(role)
            break
        else:
            sock.close()
            continue
    
    #

    # Close
    sock.close()


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 20395
    run_client(HOST, PORT)