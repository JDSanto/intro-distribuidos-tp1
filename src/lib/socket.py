class Socket:
    def __init__(self, logger):
        """
        Create the socket object
        """
        self.logger = logger

    @staticmethod
    def connect(host, port, logger):
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
