server_name = "localhost"


class Client:
    def __init__(self, port, filename, logger):
        """
        Creates the Client object, which will be used to transfer and download files to the Server.
        """
        self.port = port
        self.filename = filename
        self.logger = logger
        self.host = server_name

    def transfer_file(self, filedir):
        """
        Executes the command to transfer a file to a Server connection.
        `filedir` points to the folder of the file to be transfered.
        """
        raise NotImplementedError()

    def download_file(self, dest_folder):
        """
        Executes the command to download a file from a Server connection.
        `dest_folder` point to the destination folder where the file will be saved,
        and it'll be created creates it if it doesn't exist.
        """
        raise NotImplementedError()
