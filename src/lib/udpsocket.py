import socket
from sys import addaudithook

from lib import utils
from lib.socket import Socket
from enum import Enum


class UDPSegment:
    SEQ_NUM_SIZE = 1
    PADDING = SEQ_NUM_SIZE * 3

    def __init__(self, data, seq_num, ack, handshake):
        self.data = data
        self.seq_num = seq_num
        self.ack = ack
        self.handshake = handshake

    @staticmethod
    def pack(data, seq_number, ack=0, handshake=0):
        return UDPSegment(data, seq_number, ack, handshake)

    @staticmethod
    def unpack(data):
        seq_num = int.from_bytes(data[: UDPSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[UDPSegment.SEQ_NUM_SIZE :]

        ack = int.from_bytes(data[: UDPSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[UDPSegment.SEQ_NUM_SIZE :]

        handshake = int.from_bytes(data[: UDPSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[UDPSegment.SEQ_NUM_SIZE :]

        return UDPSegment(data, seq_num, ack, handshake)

    def to_bytes(self):
        res = self.seq_num.to_bytes(UDPSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.ack.to_bytes(UDPSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.handshake.to_bytes(UDPSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.data
        return res

    def __str__(self):
        return "seq_num: {}, ack: {}, handshake: {}, len(data): {}".format(
            self.seq_num, self.ack, self.handshake, len(self.data)
        )


class UDPSocket(Socket):

    TIMEOUT = 0.5
    N_TRIES = 10

    def __init__(self, conn_socket, addr, logger):
        self.seq_number = 0
        self.remote_number = 0
        self.tries = 0
        if conn_socket:
            conn_socket.settimeout(UDPSocket.TIMEOUT)
        super().__init__(conn_socket, addr, logger)

    @staticmethod
    def connect(host, port, logger):
        conn_socet = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsocket = UDPSocket(conn_socet, (host, port), logger)

        udpsocket.handshake_server()

        return udpsocket

    def handshake_server(self):
        """
        Handshake with the server
        """
        self.logger.debug("starting handshake...")

        while True:
            self.send_pkt(handshake=1)
            try:
                pkt = self.receive_pkt(0)
            except socket.timeout:
                self.logger.debug("got timeout. resending handshake")
                continue
            if pkt.handshake == 1 and pkt.ack == 1:
                break

        self.logger.debug(f"got pkt=[{pkt}]. sending ack")
        self.send_pkt(ack=1, seq_number=pkt.seq_num)
        self.remote_number = pkt.seq_num
        self.logger.debug("handshake done.")

    def send_pkt_conn(self, pkt):
        self.conn_socket.sendto(pkt, self.addr)

    # Send methods
    def send_pkt(self, data=b"", ack=0, handshake=0, seq_number=None):
        """
        Send data with headers through the socket
        """
        if seq_number == None:
            seq_number = self.seq_number

        pkt = UDPSegment.pack(data, seq_number, ack=ack, handshake=handshake)
        self.logger.debug(f"sending package [{pkt}]")
        self.send_pkt_conn(pkt.to_bytes())

    def send_data(self, data, retry=True, handshake=0):
        """
        Send data through the socket, creating the necessary headers.
        Waits for the corresponding ACK from the receiving end.
        """
        self.seq_number = (self.seq_number + 1) % 256
        self.send_pkt(data, handshake)
        while True:
            try:
                if self.tries == UDPSocket.N_TRIES:
                    raise Exception("Connection lost")
                pkt = self.receive_pkt(0)
            except socket.timeout:
                if not retry:
                    self.logger.debug(f"got timeout.")
                    raise socket.timeout
                self.send_pkt(data)
                self.logger.debug(f"got timeout. resending seq_num {self.seq_number}")
                self.tries += 1
                continue

            if pkt.seq_num == self.seq_number and pkt.ack:
                self.logger.debug(f"got ACK. ending. pkt=[{pkt}]")
                break
            self.logger.debug(f"old pkt=[{pkt}]. resending package.")
            if pkt.handshake:
                self.send_pkt(ack=1, seq_number=pkt.seq_num)
        self.tries = 0

    def receive_pkt_conn(self, size):
        data, addr = self.conn_socket.recvfrom(size)
        self.addr = addr
        return data

    def receive_pkt(self, buffer_size):
        """
        Receive an UDPPackage through the socket
        """
        data = self.receive_pkt_conn(buffer_size + UDPSegment.PADDING)
        return UDPSegment.unpack(data)

    def receive_data(self, buffer_size):
        """
        Receive data through the socket, removing the headers.
        Emits the corresponding ACK to the emitting end.
        """
        self.logger.debug(f"receiving more than seq_num {self.remote_number}")
        pkt = False

        while True:

            try:
                pkt = self.receive_pkt(buffer_size)
            except socket.timeout:
                self.tries += 1
                if self.tries == UDPSocket.N_TRIES:
                    raise Exception("Connection lost")
                continue

            if pkt.seq_num == ((self.remote_number + 1) % 256) and not pkt.ack:
                break

            self.logger.debug(
                f"trying to receive again. pkt=[{pkt}], remote_number={self.remote_number}"
            )

            if not pkt.ack:
                self.send_pkt(ack=1, seq_number=pkt.seq_num)

        self.logger.debug(f"got package. sending ACK. pkt=[{pkt}]")
        self.remote_number = pkt.seq_num
        self.send_pkt(ack=1, seq_number=self.remote_number)
        self.tries = 0
        return pkt.data

    def close(self):
        # TODO: Gracefull shutdown
        self.conn_socket.close()
