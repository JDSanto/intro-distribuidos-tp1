import socket
import os

from lib.server import Server
from lib.udpsocket import UDPSegment, UDPSocket


class UDPServer(Server):
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.port))
        self.logger.info(f"The server is ready to receive at {self.port}")

    def wait_for_connection(self):
        pkt = None
        udpsocket = UDPSocket(self.server_socket, None, self.logger)
        while not pkt or not pkt.handshake:
            self.logger.info("Waiting for connection...")
            try:
                pkt = udpsocket.receive_pkt(0)
            except socket.timeout:
                continue
            self.logger.info(f"got connection {pkt.to_bytes()}")

        # What happens if the handshake is a dup package?

        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn_socket.bind(("", 0))
        port = conn_socket.getsockname()[1]
        self.logger.debug(f'The server is ready to receive at {port}')

        seq_num = udpsocket.remote_number
        udpsocket = UDPSocket(conn_socket, udpsocket.addr, self.logger)
        udpsocket.remote_number = seq_num

        try:
            udpsocket.send_pkt(port.to_bytes(2, byteorder="big"), handshake=1, ack=1)
        except socket.timeout:
            self.logger.info("timeout. retrying handshake.")
            return self.wait_for_connection()

        self.logger.debug('finished handshake.')
        return udpsocket

    def stop(self):
        self.server_socket.close()

    def stop_server(self):
        self.server_socket.close()
