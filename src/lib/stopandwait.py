import socket

from lib.server import Server
from lib.socket import Socket
from lib.udpsocket import UDPSocket
from lib.udpserver import UDPServer

class SaWSegment:
    SEQ_NUM_SIZE = 1
    PADDING = SEQ_NUM_SIZE * 3

    def __init__(self, data, seq_num, ack, handshake):
        self.data = data
        self.seq_num = seq_num
        self.ack = ack
        self.handshake = handshake

    @staticmethod
    def pack(data, seq_number, ack=0, handshake=0):
        return SaWSegment(data, seq_number, ack, handshake)

    @staticmethod
    def unpack(data):
        seq_num = int.from_bytes(data[: SaWSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[SaWSegment.SEQ_NUM_SIZE :]

        ack = int.from_bytes(data[: SaWSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[SaWSegment.SEQ_NUM_SIZE :]

        handshake = int.from_bytes(data[: SaWSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[SaWSegment.SEQ_NUM_SIZE :]

        return SaWSegment(data, seq_num, ack, handshake)

    def to_bytes(self):
        res = self.seq_num.to_bytes(SaWSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.ack.to_bytes(SaWSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.handshake.to_bytes(SaWSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.data
        return res

    def __str__(self):
        return "seq_num: {}, ack: {}, handshake: {}, len(data): {}".format(
            self.seq_num, self.ack, self.handshake, len(self.data)
        )


class SaWSocket(Socket):

    TIMEOUT = 0.1
    N_TRIES = 10

    def __init__(self, conn_socket, logger):
        super().__init__(logger)
        
        self.conn_socket = conn_socket
        self.seq_number = 0
        self.remote_number = 0
        self.tries = 0
        if conn_socket:
            conn_socket.setTimeout(SaWSocket.TIMEOUT)
    
    def handshake_client(self, pkt):
        self.remote_number = pkt.seq_num

        while True:
            self.send_pkt(handshake=1, ack=1)
            try:
                pkt = self.conn_socket.receive_data()
                pkt = SaWSegment.unpack(pkt)
                self.logger.debug(f"handshake got pkt=[{pkt}]")
            except socket.timeout:
                self.logger.debug("got timeout. resending handshake")
                continue
            if pkt.handshake == 0 and pkt.ack == 1:
                break
        self.logger.debug("finished handshake.")    
    

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
        
    @staticmethod
    def connect(host, port, logger):
        udp_socket = UDPSocket.connect(host, port, logger)
        saw_socket = SaWSocket(udp_socket, logger)
        saw_socket.handshake_server()
        return saw_socket

    # Send methods
    def send_pkt(self, data=b"", ack=0, handshake=0, seq_number=None):
        """
        Send data with headers through the socket
        """
        if seq_number == None:
            seq_number = self.seq_number

        pkt = SaWSegment.pack(data, seq_number, ack=ack, handshake=handshake)
        self.logger.debug(f"sending package [{pkt}]")
        self.conn_socket.send_data(pkt.to_bytes())

    def send_data(self, data, retry=True, handshake=0):
        """
        Send data through the socket, creating the necessary headers.
        Waits for the corresponding ACK from the receiving end.
        """
        self.seq_number = (self.seq_number + 1) % 256
        self.send_pkt(data, handshake)
        while True:
            try:
                if self.tries == SaWSocket.N_TRIES:
                    raise Exception("Connection lost")
                pkt = self.receive_pkt(0)
            except socket.timeout:
                if not retry:
                    self.logger.debug(f"got timeout.")
                    raise socket.timeout
                self.logger.debug(f"got timeout. resending seq_num {self.seq_number}")
                self.send_pkt(data)
                self.tries += 1
                continue

            if pkt.seq_num == self.remote_number and not pkt.ack:
                self.logger.debug(f"got repeated package. resending ACK. pkt=[{pkt}]")
                self.send_pkt(ack=1, seq_number=pkt.seq_num)

            if pkt.seq_num == self.seq_number and pkt.ack:
                self.logger.debug(f"got ACK. ending. pkt=[{pkt}]")
                break
            
            if pkt.handshake:
                self.send_pkt(ack=1, seq_number=pkt.seq_num)
        self.tries = 0

    def receive_pkt(self, buffer_size):
        """
        Receive an UDPPackage through the socket
        """
        data = self.conn_socket.receive_data(buffer_size + SaWSegment.PADDING)
        return SaWSegment.unpack(data)

    def receive_data(self, buffer_size):
        """
        Receive data through the socket, removing the headers.
        Emits the corresponding ACK to the emitting end.
        """
        #self.logger.debug(f"receiving more than seq_num {self.remote_number}")
        pkt = False

        while True:
            try:
                pkt = self.receive_pkt(buffer_size)
                if pkt.handshake:
                    self.logger.debug(f"got a handshake package pkt=[{pkt}]...")
                    self.handshake_client(pkt)
                    continue
            except socket.timeout:
                self.tries += 1
                if self.tries == SaWSocket.N_TRIES:
                    raise Exception("Connection lost")
                continue

            if pkt.seq_num == ((self.remote_number + 1) % 256) and not pkt.ack:
                break

            self.logger.debug(
                f"trying to receive again. pkt=[{pkt}], remote_number={self.remote_number}"
            )

            if not pkt.ack:
                self.send_pkt(ack=1, seq_number=pkt.seq_num)

        self.remote_number = pkt.seq_num
        self.logger.debug(f"got package. sending ACK. pkt=[{pkt}]")
        self.send_pkt(ack=1, seq_number=self.remote_number)
        self.tries = 0
        return pkt.data

    def close(self):
        # TODO: Gracefull shutdown
        self.conn_socket.close()
        
        
class SaWServer(Server):
    def __init__(self, host, port, logger):
        self.udp_server = UDPServer(host, port, logger)
    
    def start(self):
        self.udp_server.start()

    def wait_for_connection(self):
        udp_socket = self.udp_server.wait_for_connection()
        saw_socket = SaWSocket(udp_socket, self.udp_server.logger)
        return saw_socket

    def stop_server(self):
        self.udp_server.stop_server()

    
    