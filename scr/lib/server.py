import socket
import os
DEFAULT_DEST_FOLDER = 'lib/bucket'

def start_server(port, dest_folder, logger):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)
    logger.info('The server is ready to receive')

    while True:
        connection_socket, addr = server_socket.accept()
        filename = connection_socket.recv(1024).decode()
        logger.info(f'receiving: {filename}')
        
        if not os.path.exists(dest_folder):
            dest_folder = DEFAULT_DEST_FOLDER
            logger.info('Saving file in default destination folder: {}'.format(dest_folder))
        
        with open(os.path.join(dest_folder, filename), 'wb') as f:
            while data := connection_socket.recv(1024):
                f.write(data)
