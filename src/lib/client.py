import socket
import json
import base64
import os
from lib.utils import Command

server_name = 'localhost'


def connect_socket(port):
    # TODO: try/except on connection error
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_name, port))
    return client_socket



def transfer_file(filedir, filename, port, logger):

    filepath = os.path.join(filedir, filename)

    if not os.path.isfile(filepath):
        logger.error(f'The file {filepath} does not exist')
        return

    client_socket = connect_socket(port)

    logger.info('Sending UPLOAD command')
    client_socket.send(Command.UPLOAD.value.encode())
    logger.info(f'Sending filename: {filename}')
    client_socket.send(filename.encode())
    
    logger.info('Sending file')
    with open(filepath, 'rb') as f:
        while data := f.read(1024):
            client_socket.send(data)
    
    # TODO: Check if we can/should handle a server response after file was sent
    # logger.info('Waiting for server response')
    # response = client_socket.recv(1024)
    # if response == b'ERROR':
    #     logger.error('File does not exist')


    logger.info('File uploaded')
    client_socket.close()


def download_file(dest_folder, filename, port, logger):

    if not os.path.isdir(dest_folder):
        logger.info(f'Creating destination folder: {dest_folder}')
        os.makedirs(dest_folder)


    client_socket = connect_socket(port)

    logger.info(f'Sending DOWNLOAD command')
    client_socket.send(Command.DOWNLOAD.value.encode())
    logger.info(f'Sending filename: {filename}')
    client_socket.send(filename.encode())

    logger.info('Downloading file')
    with open(os.path.join(dest_folder, filename), 'wb') as f:
        while data := client_socket.recv(1024):
            f.write(data)

    logger.info('File downloaded')
    client_socket.close()
