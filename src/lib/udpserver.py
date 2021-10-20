import socket
import os

from lib.server import Server
from lib.udpsocket import UDPSocket


class UDPServer(Server):
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.port))
        self.logger.info(f"The server is ready to receive at {self.port}")

    def wait_for_connection(self):
        _, addr = self.server_socket.recvfrom(1)
        return UDPSocket(self.server_socket, addr, self.logger)

    def stop(self):
        self.server_socket.close()

    def stop_server(self):
        self.server_socket.close()
