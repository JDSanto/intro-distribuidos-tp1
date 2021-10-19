import socket
import os
from lib import utils


class Server:
    def __init__(self, host, port, dest_folder, logger):
        """
        Creates the Server object, which will be used to receive and send files.
        `dest_folder` is the folder where the files will be saved.
        """
        self.host = host
        self.port = port
        self.dest_folder = dest_folder
        self.logger = logger

    def start(self):
        """
        Starts the server, which will wait and process client connections
        and requests.
        """
        raise NotImplementedError()

    def stop_server(self):
        """
        Stops the server.
        """
        raise NotImplementedError()
