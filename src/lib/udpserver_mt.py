import socket
import threading
import select

from lib.server import Server

MAX_DG_SIZE=(1<<16)-1

class UDPSocket:
    def __init__(self, addr, server):
        self.addr = addr;
        self.server = server
        self.condvar = threading.Condition()
        self.queue = []
    
    def _enqueue(self, data):
        with self.condvar:
            self.queue.append(data)
            self.condvar.notify(1)
            
    def send_data(self, data):
        self.server._send_data(self.addr, data)
         
    def receive_data(self, _buffer_size):
        def is_available():
            return len(self.queue) > 0
        
        with self.condvar:
            self.condvar.wait_for(is_available)
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
                    con = UDPSocket(addr, self)
                    self.connections[addr] = con
                    return con
                else:
                    self.connections[addr]._enqueue(data)
                    
        return None

    def _send_data(self, addr, data):
        with self.txlock:
            self.server_socket.sendto(data, addr)
    
    def _close(self, addr):
        del(self.connections[addr])

    def stop_server(self):
        self.server_socket.close()
        self.stopped = True
        
