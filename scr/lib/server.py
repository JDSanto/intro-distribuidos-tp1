import socket
import os
from lib.utils import Command


def upload_file(connection_socket, dest_folder, logger):
    filename = connection_socket.recv(1024).decode()
    logger.info(f'receiving: {filename}')

    if not os.path.isdir(dest_folder):
        logger.info(f'Creating destination folder: {dest_folder}')
        os.makedirs(dest_folder)

    with open(os.path.join(dest_folder, filename), 'wb') as f:
        while data := connection_socket.recv(1024):
            f.write(data)



def start_server(port, dest_folder, logger):
    # TODO: try/except on bind error
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)
    logger.info('The server is ready to receive')

    # TODO: multithreading
    while True:
        connection_socket, addr = server_socket.accept()
        command = Command(connection_socket.recv(1).decode())

        if command == Command.UPLOAD:
            upload_file(connection_socket, dest_folder, logger)

        if command == Command.DOWNLOAD:
            raise NotImplementedError('TODO')
