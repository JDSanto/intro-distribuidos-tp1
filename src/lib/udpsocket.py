import socket

from lib.socket import Socket


class UDPSocket(Socket):

    @staticmethod
    def connect(host, port, logger):
        conn_socet = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsocket = UDPSocket(conn_socet, (host, port), logger)

        # "handshake" to create the UDSocket on the server-side
        # with the client's address
        udpsocket.send_data(b'0')

        return udpsocket

    def send_data(self, data):
        self.conn_socket.sendto(data, self.addr)

    def receive_data(self, buffer_size):
        data, _ = self.conn_socket.recvfrom(buffer_size)
        return data

    def close(self):
        self.conn_socket.close()
