class Socket:

    def __init__(self, conn_socket, addr, logger):
        """
        Create the socket object with the corresponding connection
        and addres
        """
        self.conn_socket = conn_socket
        self.addr = addr
        self.logger = logger

    @staticmethod
    def connect(host, port):
        """
        Create a new Socket object connecting to a host and port
        """
        raise NotImplementedError()

    def send_data(self, data):
        raise NotImplementedError()

    def receive_data(self, buffer_size):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()
