import socket
import os

from lib.server import Server
from lib import utils


class TCPServer(Server):
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", self.port))
        self.server_socket.listen(0)
        self.logger.info("The server is ready to receive")

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
            self.logger.info(f"Creating destination folder: {self.dest_folder}")
            os.makedirs(self.dest_folder)

        # Recieve filename size and file size
        file_size = int.from_bytes(connection_socket.recv(utils.INT_SIZE), "big")
        filename_size = int.from_bytes(connection_socket.recv(utils.INT_SIZE), "big")

        # Recieve filename
        filename = connection_socket.recv(filename_size).decode()
        self.logger.info(f"Receiving file: {filename}")

        # Recieve file
        with open(os.path.join(self.dest_folder, filename), "wb") as f:
            utils.receive_file(connection_socket, f, file_size)

        self.logger.info(f"Finished uploading: {filename}")

    def send_file(self, connection_socket):
        # Recieve filename size
        filename_size = int.from_bytes(connection_socket.recv(utils.INT_SIZE), "big")

        # Recieve filename
        filename = connection_socket.recv(filename_size).decode()
        self.logger.info(f"Receiving file: {filename}")

        # Send file size
        file_size = os.path.getsize(os.path.join(self.dest_folder, filename))
        connection_socket.send(file_size.to_bytes(utils.INT_SIZE, byteorder="big"))

        # Send file
        # TODO: check if file exists, send error if it doesn't
        self.logger.info("Sending file")
        with open(os.path.join(self.dest_folder, filename), "rb") as f:
            utils.send_file(connection_socket, f, file_size)

        self.logger.info(f"Finished sending: {filename}")
        connection_socket.close()

    def stop_server(self):
        # self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()
