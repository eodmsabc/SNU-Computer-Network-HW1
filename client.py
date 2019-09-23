import socket

def run_client():
    HOST = '127.0.0.1'
    PORT = 20395
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(b'Hello World')
    data = s.recv(1024)
    print('Received: ' + str(data))


if __name__ == '__main__':
    run_client()