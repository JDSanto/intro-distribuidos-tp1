import socket

from lib import utils
from lib.socket import Socket

class UDPSocket(Socket):
    def __init__(self, conn_socket, addr, logger):
        super().__init__(logger)
        self.conn_socket = conn_socket
        self.addr = addr
    
    @staticmethod
    def connect(host, port, logger):
        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsocket = UDPSocket(conn_socket, (host, port), logger)
        return udpsocket
    
    def setTimeout(self, timeout):
        self.conn_socket.settimeout(timeout)

    def send_data(self, data):
        self.conn_socket.sendto(data, self.addr)

    def receive_data(self, buffer_size=utils.MAX_DG_SIZE):
        data, _ = self.conn_socket.recvfrom(buffer_size)
        return data

    def close(self):
        self.conn_socket.close()