import socket
import json
import base64

server_name = 'localhost'


def transfer_file(file_name, port, logger):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_name, port))
    
    client_socket.send(file_name.encode())

    with open(file_name, 'rb') as f:
        while data := f.read(1024):
            client_socket.send(data)
    
    client_socket.close()



