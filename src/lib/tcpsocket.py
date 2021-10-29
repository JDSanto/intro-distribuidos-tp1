import socket

from lib.socket import Socket


class TCPSocket(Socket):

    def __init__(self, conn_socket, addr, logger):
        super().__init__(logger)
        self.conn_socket = conn_socket
        self.addr = addr

    @staticmethod
    def connect(host, port, logger):
        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_socket.connect((host, port))
        return TCPSocket(conn_socket, (host, port), logger)

    def send_data(self, data):
        bytes_sent = 0
        while bytes_sent < len(data):
            bytes_sent += self.conn_socket.send(data[bytes_sent:])
        self.logger.debug(f'sent {bytes_sent} of {len(data)}')
        return bytes_sent

    def receive_data(self, buffer_size):
        bytes_received = 0
        data = b""
        while bytes_received < buffer_size:
            data += self.conn_socket.recv(buffer_size - bytes_received)
            bytes_received += len(data)
        self.logger.debug(f'received {bytes_received} of {buffer_size}')
        return data

    def close(self, wait=True):
        self.conn_socket.close()
