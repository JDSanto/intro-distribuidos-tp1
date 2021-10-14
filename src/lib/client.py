import socket
import json
import base64
import os
from lib.utils import *

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

        # Connect to the server
        client_socket = self.connect_socket()
        if client_socket is None:
            return

        # Send the command to the server
        self.logger.info('Sending UPLOAD command')
        client_socket.send(Command.UPLOAD.value.encode())

        # Send the filename size and the file size
        self.logger.info('Sending File size')
        file_size = os.path.getsize(filepath)
        filename_size = len(self.filename)
        client_socket.send(file_size.to_bytes(INT_SIZE, byteorder='big'))
        client_socket.send(filename_size.to_bytes(INT_SIZE, byteorder='big'))

        # Send the filename
        self.logger.info(f'Sending filename: {self.filename}')
        client_socket.send(self.filename.encode())
        
        # Send the file
        self.logger.info('Sending file')
        with open(filepath, 'rb') as f:
           send_file(client_socket, f, file_size)

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

        # Connect to the server
        client_socket = self.connect_socket()
        if client_socket is None:
            return

        # Send the command to the server
        self.logger.info(f'Sending DOWNLOAD command')
        client_socket.send(Command.DOWNLOAD.value.encode())
        
        # Send the filename size
        self.logger.info('Sending File size')
        filename_size = len(self.filename)
        client_socket.send(filename_size.to_bytes(INT_SIZE, byteorder='big'))

        # Send filename
        self.logger.info(f'Sending filename: {self.filename}')
        client_socket.send(self.filename.encode())

        # Recieve the file size
        file_size = int.from_bytes(client_socket.recv(INT_SIZE), 'big')        
    
        # Recieve the file
        self.logger.info('Downloading file')
        with open(os.path.join(dest_folder, self.filename), 'wb') as f:
            receive_file(client_socket, f, file_size)

        self.logger.info('File downloaded')
        client_socket.close()
