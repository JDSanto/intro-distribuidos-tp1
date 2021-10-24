import socket
import threading
import select

from lib.server import Server
from lib.udpsocket import UDPSocket, UDPSegment

MAX_DG_SIZE = (1 << 16) - 1


class UDPSocketHandler(UDPSocket):
    def __init__(self, addr, server, remote_number):
        super().__init__(server.server_socket, addr, server.logger)
        self.server = server
        self.condvar = threading.Condition()
        self.queue = []
        self.handshake = False
        self.remote_number = remote_number
        self.handshake_client()

    def handshake_client(self):

        while True:
            super().send_pkt(handshake=1, ack=1)
            try:
                pkt = super().receive_pkt_conn(MAX_DG_SIZE)
                pkt = UDPSegment.unpack(pkt)
                self.logger.debug(f"handshake got pkt=[{pkt}]")
            except socket.timeout:
                self.logger.debug("got timeout. resending handshake")
                continue
            if pkt.handshake == 0 and pkt.ack == 1:
                break
        self.logger.debug("finished handshake.")

    def _enqueue(self, data):
        with self.condvar:
            self.queue.append(data)
            self.condvar.notify(1)

    def send_pkt_conn(self, data):
        self.server._send_data(self.addr, data)

    def receive_pkt_conn(self, _buffer_size):
        def is_available():
            return len(self.queue) > 0

        with self.condvar:
            if not self.condvar.wait_for(is_available, timeout=UDPSocket.TIMEOUT):
                raise socket.timeout
            return self.queue.pop(0)

    def close(self):
        self.server._close(self.addr)


class UDPServerMT(Server):
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.port))
        self.server_socket.setblocking(False)
        self.logger.info(f"The server is ready to receive at {self.port}")

        self.connections = {}
        self.txlock = threading.Lock()
        self.stopped = False

    def wait_for_connection(self):
        while not self.stopped:
            ready = select.select([self.server_socket], [], [], 1)
            if ready[0]:
                data, addr = self.server_socket.recvfrom(MAX_DG_SIZE)

                if not addr in self.connections:
                    pkt = UDPSegment.unpack(data)
                    if not pkt.handshake:
                        continue
                    self.logger.debug(f"got a handshake package pkt=[{pkt}]...")
                    con = UDPSocketHandler(addr, self, pkt.seq_num)
                    self.connections[addr] = con
                    return con
                else:
                    self.connections[addr]._enqueue(data)

        return None

    def _send_data(self, addr, data):
        with self.txlock:
            self.server_socket.sendto(data, addr)

    def _close(self, addr):
        del self.connections[addr]

    def stop_server(self):
        self.server_socket.close()
        self.stopped = True
