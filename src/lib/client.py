import socket
import json
import base64
import os
from lib.utils import Command

server_name = 'localhost'

class Client:
    def __init__(self, port, filename, logger):
        '''
        Creates the Client object, which will be used to transfer and download files to the Server.
        '''
        self.port = port
        self.filename = filename
        self.logger = logger

    def transfer_file(self, filedir):
        '''
        Executes the command to transfer a file to a Server connection.
        `filedir` points to the folder of the file to be transfered.
        '''
        raise NotImplementedError()
    
    def download_file(self, dest_folder):
        '''
        Executes the command to download a file from a Server connection.
        `dest_folder` point to the destination folder where the file will be saved,
        and it'll be created creates it if it doesn't exist.
        '''
        raise NotImplementedError()

class TCPClient(Client):

    def connect_socket(self):
        try:    
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_name, self.port))
        except socket.error as e:
            self.logger.error(f'Error connecting to server: {e}')
            return None
        return client_socket


    def transfer_file(self, filedir):
        filepath = os.path.join(filedir, self.filename)
        if not os.path.isfile(filepath):
            self.logger.error(f'The file {filepath} does not exist')
            return

        client_socket = self.connect_socket()
        if client_socket is None:
            return

        self.logger.info('Sending UPLOAD command')
        client_socket.send(Command.UPLOAD.value.encode())
        self.logger.info(f'Sending filename: {self.filename}')
        client_socket.send(self.filename.encode())
        
        self.logger.info('Sending file')
        with open(filepath, 'rb') as f:
            while data := f.read(1024):
                client_socket.send(data)
        
        # TODO: Check if we can/should handle a server response after file was sent
        # logger.info('Waiting for server response')
        # response = client_socket.recv(1024)
        # if response == b'ERROR':
        #     logger.error('File does not exist')

        self.logger.info('File uploaded')
        client_socket.close()

    def download_file(self, dest_folder):
        if not os.path.isdir(dest_folder):
            self.logger.info(f'Creating destination folder: {dest_folder}')
            os.makedirs(dest_folder)

        client_socket = self.connect_socket()
        if client_socket is None:
            return

        self.logger.info(f'Sending DOWNLOAD command')
        client_socket.send(Command.DOWNLOAD.value.encode())
        self.logger.info(f'Sending filename: {self.filename}')
        client_socket.send(self.filename.encode())

        self.logger.info('Downloading file')
        with open(os.path.join(dest_folder, self.filename), 'wb') as f:
            while data := client_socket.recv(1024):
                f.write(data)

        self.logger.info('File downloaded')
        client_socket.close()
