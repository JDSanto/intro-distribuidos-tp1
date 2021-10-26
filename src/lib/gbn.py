import socket

from lib.server import Server
from lib.udpsocket import UDPSocket
from lib.udpserver import UDPServer
from lib.rdt import RDTSegment, RDTSocket


class GBNSocket(RDTSocket):
    N = 10

    def __init__(self, conn_socket, logger):
        super().__init__(conn_socket, logger)
        self.in_flight = []

    @staticmethod
    def connect(host, port, logger):
        udp_socket = UDPSocket.connect(host, port, logger)
        rdt_socket = GBNSocket(udp_socket, logger)
        # rdt_socket.handshake_server()
        return rdt_socket

    def send_data(self, data):
        sent = False

        # If there is root in the window sent the pkt
        if len(self.in_flight) < GBNSocket.N:
            self.seq_number = RDTSegment.increment(self.seq_number)
            pkt = self.send_pkt(data)
            self.in_flight.append((pkt.seq_num, data))
            sent = True
        else:
            self.logger.debug("window is full.")

        # Process ACKS without blocking
        pkt = self.receive_pkt(1000, wait=False)
        while pkt is not None:
            self.process_ack(pkt)
            pkt = self.receive_pkt(0, wait=False)

        # If the window was full
        if not sent:
            self.await_ack()
            # reattempt to send after wait
            self.send_data(data)

    def process_ack(self, pkt):
        if pkt.ack:
            self.logger.debug(f"got ACK. ending. pkt=[{pkt}]")
            while len(self.in_flight):
                if pkt.seq_num >= self.in_flight[0][0]:
                    self.in_flight.pop(0)
                    return True
                else:
                    break
        else:
            # If the pkt was not an ack then it is dropped.
            self.logger.debug(f"Got unexpected data pkt [{pkt}]. Dropped.")
            self.send_pkt(ack=1, seq_number=self.remote_number)

        return False

    def await_ack(self):
        try:
            pkt = self.receive_pkt(0, wait=True)
            if self.process_ack(pkt):
                self.tries = 0
        except socket.timeout:
            # Re-send unacknowledged pkts
            self.logger.debug(f"got timeout. resending from seq_num {self.in_flight[0][0]}")
            self.tries += 1
            for (seq_num, data) in self.in_flight:
                pkt = self.send_pkt(data, seq_number=seq_num)

    def await_empty_send_queue(self):
        while len(self.in_flight):
            self.logger.debug(
                f"Still {len(self.in_flight)} packets in flight. {self.in_flight[0][0]} to {self.in_flight[-1][0]}")
            self.await_ack()
            if self.tries == RDTSocket.N_TRIES:
                raise Exception("Connection lost")

    def receive_data(self, buffer_size):
        # Wait to confirm in flight pkts before sending
        self.await_empty_send_queue()
        return RDTSocket.receive_data(self, buffer_size)

    def close(self):
        # Wait to confirm in flight pkts before closing
        self.await_empty_send_queue()

        # Wait for resends due to lost outgoing acks
        self.tries = 0
        while self.tries < RDTSocket.N_TRIES:
            try:
                pkt = self.receive_pkt(0)
                self.process_ack(pkt)
            except socket.timeout:
                self.tries += 1
                pass

        RDTSocket.close(self)


class GBNServer(Server):
    def __init__(self, host, port, logger):
        self.udp_server = UDPServer(host, port, logger)

    def start(self):
        self.udp_server.start()

    def wait_for_connection(self):
        udp_socket = self.udp_server.wait_for_connection()
        return GBNSocket(udp_socket, self.udp_server.logger)

    def stop_server(self):
        self.udp_server.stop_server()
