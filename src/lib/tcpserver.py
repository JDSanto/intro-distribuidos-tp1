import socket

from lib.server import Server
from lib.tcpsocket import TCPSocket


class TCPServer(Server):

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.port))
        self.server_socket.listen(0)
        self.logger.info("The server is ready to receive")

    def wait_for_connection(self):
        connection_socket, addr = self.server_socket.accept()
        return TCPSocket(connection_socket, addr)

    def stop_server(self):
        self.server_socket.close()
