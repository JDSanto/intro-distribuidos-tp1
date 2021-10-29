import socket
import threading
import select

from lib import utils
from lib.server import Server
from lib.socket import Socket


class UDPSocketMT(Socket):
    def __init__(self, addr, server):
        super().__init__(server.logger)
        self.server = server
        self.addr = addr
        self.condvar = threading.Condition()
        self.queue = []
        self.timeout = None

    def _enqueue(self, data):
        with self.condvar:
            self.queue.append(data)
            self.condvar.notify(1)

    def setTimeout(self, timeout):
        self.timeout = timeout

    def send_data(self, data):
        self.server._send_data(self.addr, data)

    def receive_data(self, _buffer_size=None, wait=True):
        def is_available():
            return len(self.queue) > 0

        with self.condvar:
            if wait:
                if not self.condvar.wait_for(is_available, timeout=self.timeout):
                    raise socket.timeout
                return self.queue.pop(0)
            else:
                if is_available():
                    return self.queue.pop(0)
                else:
                    return None

    def close(self, wait=False):
        self.server._close(self.addr)


class UDPServer(Server):
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
                data, addr = self.server_socket.recvfrom(utils.MAX_DG_SIZE)

                new_con = None
                if addr not in self.connections:
                    new_con = UDPSocketMT(addr, self)
                    self.connections[addr] = new_con
                    self.logger.info(f"New connection from {addr}")

                self.connections[addr]._enqueue(data)

                if new_con:
                    return new_con

        return None

    def _send_data(self, addr, data):
        with self.txlock:
            self.server_socket.sendto(data, addr)

    def _close(self, addr):
        del self.connections[addr]

    def stop_server(self):
        self.server_socket.close()
        self.stopped = True
