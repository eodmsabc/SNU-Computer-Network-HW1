# socket interface

import socket

def send_to(sock, tp, data=''):
    concat = tp + ' ' + data.strip()
    data_b = concat.encode()
    sock.sendall(data_b)

def read_from(conn):
    data_b = conn.recv(1024)
    data = data_b.decode("utf-8")
    r = data.split(' ')
    return {"type": r[0], "data": r[1:]}
