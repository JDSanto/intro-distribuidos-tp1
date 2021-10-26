import socket
from lib.socket import Socket


class RDTSegment:
    SEQ_NUM_SIZE = 2
    PADDING = SEQ_NUM_SIZE * 2 + 1

    def __init__(self, data, seq_num, ack, handshake):
        self.data = data
        self.seq_num = seq_num
        self.ack = ack
        self.handshake = handshake

    @staticmethod
    def pack(data, seq_number, ack=0, handshake=0):
        return RDTSegment(data, seq_number, ack, handshake)

    @staticmethod
    def unpack(data):
        seq_num = int.from_bytes(data[: RDTSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[RDTSegment.SEQ_NUM_SIZE:]

        ack = int.from_bytes(data[: RDTSegment.SEQ_NUM_SIZE], byteorder="big")
        data = data[RDTSegment.SEQ_NUM_SIZE:]

        handshake = int.from_bytes(data[: 1], byteorder="big")
        data = data[1:]

        return RDTSegment(data, seq_num, ack, handshake)

    def to_bytes(self):
        res = self.seq_num.to_bytes(RDTSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.ack.to_bytes(RDTSegment.SEQ_NUM_SIZE, byteorder="big")
        res += self.handshake.to_bytes(1, byteorder="big")
        res += self.data
        return res

    def __str__(self):
        return "seq_num: {}, ack: {}, handshake: {}, len(data): {}".format(
            self.seq_num, self.ack, self.handshake, len(self.data)
        )

    @staticmethod
    def increment(seq_num):
        return (seq_num + 1) % (1 << 8 * RDTSegment.SEQ_NUM_SIZE)


class RDTSocket(Socket):
    TIMEOUT = 0.05
    N_TRIES = 10

    def __init__(self, conn_socket, logger):
        super().__init__(logger)

        self.conn_socket = conn_socket
        self.seq_number = 0
        self.remote_number = 0
        self.tries = 0
        if conn_socket:
            conn_socket.setTimeout(RDTSocket.TIMEOUT)

    def handshake_client(self):
        self.logger.debug("starting handshake...")
        pkt = self.receive_pkt(0, wait=False)

        if pkt.handshake:
            self.remote_number = pkt.seq_num

            while True:
                self.send_pkt(handshake=1, ack=1)
                try:
                    pkt = self.conn_socket.receive_data()
                    pkt = RDTSegment.unpack(pkt)
                    self.logger.debug(f"handshake got pkt=[{pkt}]")
                except socket.timeout:
                    self.tries += 1
                    if self.tries == RDTSocket.N_TRIES:
                        raise Exception("Connection lost")
                    self.logger.debug("got timeout. resending handshake")
                    continue

                if pkt.handshake == 0 and pkt.ack == 1:
                    self.tries = 0
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
                self.tries += 1
                if self.tries == RDTSocket.N_TRIES:
                    raise Exception("Connection lost")
                self.logger.debug("got timeout. resending handshake")
                continue
            if pkt.handshake == 1 and pkt.ack == 1:
                self.tries = 0
                break

        self.logger.debug(f"got pkt=[{pkt}]. sending ack")
        self.send_pkt(ack=1, seq_number=pkt.seq_num)
        self.remote_number = pkt.seq_num
        self.logger.debug("handshake done.")

    # Send methods
    def send_pkt(self, data=b"", ack=0, handshake=0, seq_number=None):
        """
        Send data with headers through the socket
        """
        if seq_number is None:
            seq_number = self.seq_number

        pkt = RDTSegment.pack(data, seq_number, ack=ack, handshake=handshake)
        self.logger.debug(f"sending package [{pkt}]")
        self.conn_socket.send_data(pkt.to_bytes())
        return pkt

    def receive_pkt(self, buffer_size, wait=True):
        """
        Receive an UDPPackage through the socket
        """
        data = self.conn_socket.receive_data(buffer_size + RDTSegment.PADDING, wait)
        return RDTSegment.unpack(data) if data else None

    def receive_data(self, buffer_size):
        """
        Receive data through the socket, removing the headers.
        Emits the corresponding ACK to the emitting end.
        """
        # self.logger.debug(f"receiving more than seq_num {self.remote_number}")
        pkt = False

        while True:
            try:
                pkt = self.receive_pkt(buffer_size)
            except socket.timeout:
                self.tries += 1
                if self.tries == RDTSocket.N_TRIES:
                    raise Exception("Connection lost")
                self.logger.debug("got timeout receiving. retrying")
                continue

            if pkt.seq_num == RDTSegment.increment(self.remote_number) and not pkt.ack:
                break

            self.logger.debug(
                f"Expecting remote_number={self.remote_number}. Got pkt=[{pkt}]"
            )

            if not pkt.ack:
                self.send_pkt(ack=1, seq_number=self.remote_number)

        self.remote_number = pkt.seq_num
        self.logger.debug(f"got package. sending ACK. pkt=[{pkt}]")
        self.send_pkt(ack=1, seq_number=self.remote_number)
        self.tries = 0
        return pkt.data

    def close(self):
        # TODO: Gracefull shutdown
        self.conn_socket.close()
