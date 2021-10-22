import socket
from sys import addaudithook

from lib import utils
from lib.socket import Socket
from enum import Enum


# def calculate_checksum(data):
#     """
#     Calculates the checksum for a given byte sequence
#     """
#     return sum(data) % 256 ** UDPSegment.CHECKSUM_SIZE


class UDPSegment():
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
        seq_num = int.from_bytes(data[:UDPSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[UDPSegment.SEQ_NUM_SIZE:]

        ack = int.from_bytes(data[:UDPSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[UDPSegment.SEQ_NUM_SIZE:]

        handshake = int.from_bytes(data[:UDPSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[UDPSegment.SEQ_NUM_SIZE:]

        return UDPSegment(data, seq_num, ack, handshake)

    def to_bytes(self):
        res = self.seq_num.to_bytes(UDPSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.ack.to_bytes(UDPSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.handshake.to_bytes(UDPSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.data
        return res




class UDPSocket(Socket):

    def __init__(self, conn_socket, addr, logger):
        self.seq_number = 0
        conn_socket.settimeout(0.5)
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
        self.logger.debug('starting handshake...')
        self.seq_number = 1
        pkt = UDPSegment.pack(b'', self.seq_number, ack=0, handshake=1)
        try:
            self.conn_socket.sendto(pkt.to_bytes(), self.addr)
        # TODO: What if the first handshake is lost?
        # check if this solution is good enough, even if quite ugly
        except socket.timeout:
            self.handshake_server()
            return
        self.logger.debug('sent first handshake message')
        while True:
            try:
                pkt = self.receive_pkt(2)
            except socket.timeout:
                continue
            if pkt.seq_num == self.seq_number and not pkt.ack:
                self.logger.debug('got port number. continuing handshake')
                break
            self.logger.debug(f'got package {pkt.ack}, {pkt.seq_num} != {self.seq_number}. resending ACK')
        port = int.from_bytes(pkt.data, byteorder="big")
        self.addr = (self.addr[0], port)
        self.logger.debug(f'handshake done. port={port} bytes={pkt.data}')
        self.send_ack(self.seq_number)


    # Send methods
    def send_pkt(self, data):
        """
        Send data with headers through the socket
        """
        # FIXME: name plz
        self.logger.debug(f'trying to send package {self.seq_number}')
        pkt = UDPSegment.pack(data, self.seq_number).to_bytes()
        self.conn_socket.sendto(pkt, self.addr)

    def send_ack(self, seq_num):
        self.logger.debug(f'trying to send ack {self.seq_number}')
        pkt = UDPSegment.pack(b'', seq_num, ack=1).to_bytes()
        self.conn_socket.sendto(pkt, self.addr)


    def send_data(self, data, retry=True):
        """
        Send data through the socket, creating the necessary headers
        """
        self.seq_number = (self.seq_number + 1) % 256
        self.logger.debug(f'sending seq_num {self.seq_number}. waiting for ACK')

        self.send_pkt(data)
        while True:
            try:
                pkt = self.receive_ack()
            except socket.timeout:
                self.logger.debug(f'got timeout. resending seq_num {self.seq_number}')
                self.send_pkt(data)
                if not retry:
                    raise socket.timeout
                continue
            if pkt.seq_num == self.seq_number and pkt.ack:
                self.logger.debug(f'got ACK. ending')
                break
            self.logger.debug(f'old ack={pkt.ack}, {pkt.seq_num} != {self.seq_number} obtained. resending package')
            # self.send_pkt(data)


    # Receive methods
    def receive_ack(self):
        self.logger.debug(f'trying to receive ack {self.seq_number}')
        data, addr = self.conn_socket.recvfrom(UDPSegment.PADDING)
        self.addr = addr
        return UDPSegment.unpack(data)

    def receive_pkt(self, buffer_size):
        """
        Receive an UDPPackage through the socket
        """
        self.logger.debug(f'trying to receiving package after {self.seq_number}')
        data, addr = self.conn_socket.recvfrom(buffer_size + UDPSegment.PADDING)
        self.addr = addr
        return UDPSegment.unpack(data)



    def receive_data(self, buffer_size):
        """
        Receive data through the socket, removing the headers
        """
        self.logger.debug(f'receiving more than seq_num {self.seq_number}')
        try:
            pkt = self.receive_pkt(buffer_size)
        except socket.timeout:
            return self.receive_data(buffer_size)

        # while not (pkt.seq_num == ((self.seq_number + 1) % 256) and not pkt.ack):
        while pkt.seq_num != ((self.seq_number + 1) % 256) or pkt.ack:
            try:
                if not pkt.ack:
                    self.send_ack(pkt.seq_num)
                pkt = self.receive_pkt(buffer_size)
            except socket.timeout:
                self.logger.debug(f'timeout on package. trying again (self.seq_num={self.seq_number}, pkt.seq_num={pkt.seq_num})')
                pass

        self.logger.debug(f'got package {pkt.seq_num}. sending ACK.')
        self.seq_number = pkt.seq_num
        self.send_ack(self.seq_number)
        return pkt.data

    def close(self):
        self.conn_socket.close()
