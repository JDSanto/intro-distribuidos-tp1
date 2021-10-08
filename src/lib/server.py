import socket
import os
from lib.utils import Command

class Server:
    def __init__(self, host, port, dest_folder, logger):
        '''
        Creates the Server object, which will be used to receive and send files.
        `dest_folder` is the folder where the files will be saved.
        '''
        self.host = host
        self.port = port
        self.dest_folder = dest_folder
        self.logger = logger
   
    def start_server(self):
        '''
        Starts the server, which will wait and process client connections
        and requests.
        '''
        raise NotImplementedError()

    def stop_server(self):
        '''
        Stops the server.
        '''

    # def receive_file(self, client_socket):
    #     '''
    #     Executes the command to receive a file from a client connection.
    #     '''
    #     raise NotImplementedError()

    # def send_file(self, client_socket):
    #     '''
    #     Executes the command to send a file to a client connection.
    #     '''
    #     raise NotImplementedError()


class TCPServer(Server):

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(1)
        self.logger.info('The server is ready to receive')

        # TODO: multithreading
        while True:
            connection_socket, addr = self.server_socket.accept()
            command = Command(connection_socket.recv(1).decode())

            if command == Command.UPLOAD:
                self.receive_file(connection_socket)

            if command == Command.DOWNLOAD:
                self.send_file(connection_socket)

    def receive_file(self, connection_socket):
        filename = connection_socket.recv(1024).decode()
        self.logger.info(f'Receiving file: {filename}')

        if not os.path.isdir(self.dest_folder):
            self.logger.info(f'Creating destination folder: {self.dest_folder}')
            os.makedirs(self.dest_folder)

        with open(os.path.join(self.dest_folder, filename), 'wb') as f:
            while data := connection_socket.recv(1024):
                f.write(data)

        self.logger.info(f'Finished uploading: {filename}')

    def send_file(self, connection_socket):
        filename = connection_socket.recv(1024).decode()
        self.logger.info(f'Receiving file: {filename}')

        # TODO: check if file exists, send error if it doesn't
        self.logger.info('Sending file')
        with open(os.path.join(self.dest_folder, filename), 'rb') as f:
            while data := f.read(1024):
                connection_socket.send(data)

        self.logger.info(f'Finished sending: {filename}')
        connection_socket.close()

    def stop_server(self):
        # self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()
        