import socket
import os

from lib.client import Client
from lib import utils


class UDPClient(Client):
    def connect_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def transfer_file(self, filedir):
        filepath = os.path.join(filedir, self.filename)
        if not os.path.isfile(filepath):
            self.logger.error(f"The file {filepath} does not exist")
            return

        client_socket = self.connect_socket()

        # Send the command to the server
        self.logger.info("Sending UPLOAD command")
        client_socket.sendto(
            utils.Command.UPLOAD.value, (self.host, self.port)
        )

        # Send the filename size and the file size
        self.logger.info("Sending File size")
        file_size = os.path.getsize(filepath)
        filename_size = len(self.filename)
        client_socket.sendto(
            file_size.to_bytes(utils.INT_SIZE, byteorder="big"), (self.host, self.port)
        )
        client_socket.sendto(
            filename_size.to_bytes(utils.INT_SIZE, byteorder="big"),
            (self.host, self.port),
        )

        # Send the filename
        self.logger.info(f"Sending filename: {self.filename}")
        client_socket.sendto(self.filename.encode(), (self.host, self.port))

        # Send the file
        self.logger.info("Sending file")
        with open(filepath, "rb") as f:
            while data := f.read(utils.MSG_SIZE):
                client_socket.sendto(data, (self.host, self.port))

        self.logger.info('Waiting for server response')
        response = client_socket.recvfrom(1)
        if response == utils.Status.ERROR.value:
            self.logger.error('File transfer failed')
        else:
            self.logger.info("File uploaded")

        client_socket.close()

    def download_file(self, dest_folder):
        if not os.path.isdir(dest_folder):
            self.logger.info(f"Creating destination folder: {dest_folder}")
            os.makedirs(dest_folder)

        client_socket = self.connect_socket()

        # Send the command to the server
        self.logger.info(f"Sending DOWNLOAD command")
        client_socket.sendto(
            utils.Command.DOWNLOAD.value, (self.host, self.port)
        )

        # Send the filename size
        self.logger.info("Sending File size")
        filename_size = len(self.filename)
        client_socket.sendto(
            filename_size.to_bytes(utils.INT_SIZE, byteorder="big"),
            (self.host, self.port),
        )

        # Send filename
        self.logger.info(f"Sending filename: {self.filename}")
        client_socket.sendto(self.filename.encode(), (self.host, self.port))

        # Recieve the file size
        file_size = int.from_bytes(client_socket.recv(utils.INT_SIZE), "big")

        # Recieve the file
        self.logger.info("Downloading file")
        with open(os.path.join(dest_folder, self.filename), "wb") as f:
            while file_size > 0:
                data = client_socket.recvfrom(min(utils.MSG_SIZE, file_size))[0]
                f.write(data)
                file_size -= len(data)

        self.logger.info("File downloaded")
        client_socket.sendto(utils.Status.OK.value, (self.host, self.port))
        client_socket.close()
