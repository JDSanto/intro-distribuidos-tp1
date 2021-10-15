import socket
import os
from lib import utils

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


class UDPServer(Server):

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('', self.port))

        # TODO: multithreading (a bit harder in UDP)
        while True:
            message, addr = self.server_socket.recvfrom(1)
            command = utils.Command(message.decode())

            # TODO: set a unique socket for the incoming connection
            if command == utils.Command.UPLOAD:
                self.receive_file(addr)

            if command == utils.Command.DOWNLOAD:
                self.send_file(addr)

            else:
                self.logger.info(f'Unknown command: {command}')


    def receive_file(self, addr):
        if not os.path.isdir(self.dest_folder):
            self.logger.info(f'Creating destination folder: {self.dest_folder}')
            os.makedirs(self.dest_folder)

        # Recieve filename size and file size
        file_size = int.from_bytes(self.server_socket.recvfrom(utils.INT_SIZE)[0], 'big')
        filename_size = int.from_bytes(self.server_socket.recvfrom(utils.INT_SIZE)[0], 'big')
        
        # Recieve filename
        filename = self.server_socket.recvfrom(filename_size)[0].decode()
        self.logger.info(f'Receiving file: {filename}')

        # Recieve file
        with open(os.path.join(self.dest_folder, filename), 'wb') as f:
            while file_size > 0:
                data = self.server_socket.recvfrom(min(utils.MSG_SIZE, file_size))[0]
                f.write(data)
                file_size -= len(data)
            # utils.receive_file(connection_socket, f, file_size)
            
        self.logger.info(f'Finished uploading: {filename}')


    def send_file(self, addr):
        # Recieve filename size
        filename_size = int.from_bytes(self.server_socket.recvfrom(utils.INT_SIZE)[0], 'big')

        # Recieve filename
        filename = self.server_socket.recvfrom(filename_size)[0].decode()
        self.logger.info(f'Receiving file: {filename}')

        # Send file size
        file_size = os.path.getsize(os.path.join(self.dest_folder, filename))
        self.server_socket.sendto(file_size.to_bytes(utils.INT_SIZE, byteorder='big'), addr)
        
        # Send file
        # TODO: check if file exists, send error if it doesn't
        self.logger.info('Sending file')
        with open(os.path.join(self.dest_folder, filename), 'rb') as f:
            while file_size > 0:
                data = f.read(utils.MSG_SIZE)
                self.server_socket.sendto(data, addr)
                file_size -= len(data)

        self.logger.info(f'Finished sending: {filename}')
    

    def stop_server(self):
        # self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()



class TCPServer(Server):

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(0)
        self.logger.info('The server is ready to receive')

        # TODO: multithreading
        while True:
            connection_socket, addr = self.server_socket.accept()
            command = utils.Command(connection_socket.recv(1).decode())

            if command == utils.Command.UPLOAD:
                self.receive_file(connection_socket)

            if command == utils.Command.DOWNLOAD:
                self.send_file(connection_socket)

    def receive_file(self, connection_socket):
        if not os.path.isdir(self.dest_folder):
            self.logger.info(f'Creating destination folder: {self.dest_folder}')
            os.makedirs(self.dest_folder)

        # Recieve filename size and file size
        file_size = int.from_bytes(connection_socket.recv(utils.INT_SIZE), 'big')
        filename_size = int.from_bytes(connection_socket.recv(utils.INT_SIZE), 'big')
        
        # Recieve filename
        filename = connection_socket.recv(filename_size).decode()
        self.logger.info(f'Receiving file: {filename}')

        # Recieve file
        with open(os.path.join(self.dest_folder, filename), 'wb') as f:
            utils.receive_file(connection_socket, f, file_size)
            
        self.logger.info(f'Finished uploading: {filename}')

    def send_file(self, connection_socket):
        # Recieve filename size
        filename_size = int.from_bytes(connection_socket.recv(utils.INT_SIZE), 'big')        
        
        # Recieve filename
        filename = connection_socket.recv(filename_size).decode()
        self.logger.info(f'Receiving file: {filename}')

        # Send file size
        file_size = os.path.getsize(os.path.join(self.dest_folder, filename))
        connection_socket.send(file_size.to_bytes(utils.INT_SIZE, byteorder='big'))
        
        # Send file
        # TODO: check if file exists, send error if it doesn't
        self.logger.info('Sending file')
        with open(os.path.join(self.dest_folder, filename), 'rb') as f:
            utils.send_file(connection_socket, f, file_size)

        self.logger.info(f'Finished sending: {filename}')
        connection_socket.close()

    def stop_server(self):
        # self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()
        