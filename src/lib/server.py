
class Server:
    def __init__(self, host, port, logger):
        """
        Creates the Server object, which will be used to receive and send files.
        `dest_folder` is the folder where the files will be saved.
        """
        self.host = host
        self.port = port
        self.logger = logger

    def start(self):
        """
        Starts the server, which will wait and process client connections
        and requests.
        """
        raise NotImplementedError()

    def wait_for_connection(self):
        raise NotImplementedError()

    def stop_server(self):
        """
        Stops the server.
        """
        raise NotImplementedError()
