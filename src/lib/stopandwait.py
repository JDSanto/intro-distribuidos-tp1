import socket

from lib.rdt import RDTSegment, RDTSocket
from lib.server import Server
from lib.udpserver import UDPServer
from lib.udpsocket import UDPSocket


class SaWSocket(RDTSocket):
    @staticmethod
    def connect(host, port, logger):
        udp_socket = UDPSocket.connect(host, port, logger)
        rdt_socket = SaWSocket(udp_socket, logger)
        return rdt_socket

    def send_data(self, data, retry=True):
        """
        Send data through the socket, creating the necessary headers.
        Waits for the corresponding ACK from the receiving end.
        """
        self.seq_number = RDTSegment.increment(self.seq_number)
        self.send_pkt(data)
        while True:
            try:
                if self.tries == RDTSocket.N_TRIES:
                    raise Exception("Connection lost")
                pkt = self.receive_pkt(0)
            except socket.timeout:
                if not retry:
                    self.logger.debug("got timeout.")
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

        self.tries = 0

    def close(self, wait=False):
        self.logger.debug("Closing SaW socket")
        RDTSocket.close(self, wait)


class SaWServer(Server):
    def __init__(self, host, port, logger):
        self.udp_server = UDPServer(host, port, logger)

    def start(self):
        self.udp_server.start()

    def wait_for_connection(self):
        udp_socket = self.udp_server.wait_for_connection()
        return SaWSocket(udp_socket, self.udp_server.logger)

    def stop_server(self):
        self.udp_server.stop_server()
