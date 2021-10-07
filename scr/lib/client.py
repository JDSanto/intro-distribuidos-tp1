import socket
import json
import base64
import os
from lib.utils import Command

server_name = 'localhost'


def transfer_file(file_path, port, logger):

    if not os.path.isfile(file_path):
        logger.error(f'The file {file_dir} does not exist')
        client_socket.close()
        return

    # TODO: try/except on connection error
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_name, port))

    logger.info("Send Command")
    client_socket.send(Command.UPLOAD.value.encode())
    logger.info("Send File")
    client_socket.send(file_path.encode())
    logger.info("File recived")
    
    with open(file_path, 'rb') as f:
        while data := f.read(1024):
            client_socket.send(data)
    
    response = client_socket.recv(1024)
    if response == b'ERROR':
        logger.error('File does not exist')


    client_socket.close()



