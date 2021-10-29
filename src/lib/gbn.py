import socket

from lib.server import Server
from lib.udpsocket import UDPSocket
from lib.udpserver import UDPServer
from lib.rdt import RDTSegment, RDTSocket


class GBNSocket(RDTSocket):
    WINDOW_SIZE = 10

    def __init__(self, conn_socket, logger):
        super().__init__(conn_socket, logger)
        self.in_flight = []

    @staticmethod
    def connect(host, port, logger):
        udp_socket = UDPSocket.connect(host, port, logger)
        rdt_socket = GBNSocket(udp_socket, logger)
        return rdt_socket

    def send_data(self, data=b""):
        """
        Send data through the socket, creating the necessary headers.
        If an ACK is not received, the packet is added to the in-flight list.
        If the in-flight list is full, awaits ACKs for packages in the list.
        """
        sent = False

        # If there is room in the window sent the pkt
        if len(self.in_flight) < GBNSocket.WINDOW_SIZE:
            self.seq_number = RDTSegment.increment(self.seq_number)
            pkt = self.send_pkt(data)
            self.in_flight.append(pkt)
            sent = True
        else:
            self.logger.debug("window is full.")

        # Process ACKS without blocking
        pkt = self.receive_pkt(1000, blocking=False)
        while pkt is not None:
            self.process_ack(pkt)
            pkt = self.receive_pkt(0, blocking=False)

        # If the window was full => block until there is room
        if not sent:
            if len(self.in_flight) == GBNSocket.WINDOW_SIZE:
                self.await_ack()
            # reattempt to send after wait
            self.send_data(data)

    def process_ack(self, pkt):
        """
        Process a packet. If it's an ACK, remove it and all previous ones
        from the in-flight list and return True.
        """
        if pkt.ack:
            self.logger.debug(f"got ACK. ending. pkt=[{pkt}]")
            for i in range(len(self.in_flight)):
                if self.in_flight[i].seq_num == pkt.seq_num:
                    self.in_flight = self.in_flight[i + 1 :]
                    return True
        else:
            # If the pkt was not an ack then it is dropped.
            self.logger.debug(f"Got unexpected data pkt [{pkt}]. Dropped.")
            self.send_pkt(ack=1, seq_number=self.remote_number)

        return False

    def await_ack(self):
        """
        Waits and processes an ACK packet. If a timeout occurs without any new
        ACK from the in-flight list, resend the packets in the list.
        """
        try:
            pkt = self.receive_pkt(0)
            if self.process_ack(pkt):
                self.tries = 0
        except socket.timeout:
            if not self.in_flight:
                return
            # Re-send unacknowledged pkts
            self.logger.debug(
                f"got timeout. resending from seq_num {self.in_flight[0].seq_num}"
            )
            self.tries += 1
            for pkt in self.in_flight:
                self.send_pkt(pkt.data, seq_number=pkt.seq_num)

    def await_empty_send_queue(self):
        """
        Send all packets in the in-flight list, awaiting ACKs.
        """
        while len(self.in_flight):
            self.logger.debug(
                (
                    f"Still {len(self.in_flight)} packets in flight. "
                    f"{self.in_flight[0].seq_num} to {self.in_flight[-1].seq_num}"
                )
            )
            self.await_ack()
            if self.tries == RDTSocket.N_TRIES:
                raise Exception("Connection lost")

    def receive_data(self, buffer_size):
        # Wait to confirm in flight pkts before sending
        self.await_empty_send_queue()
        return RDTSocket.receive_data(self, buffer_size)

    def close(self, wait=False):
        self.logger.debug("Closing GBN socket")

        self.await_empty_send_queue()

        RDTSocket.close(self, wait)


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
