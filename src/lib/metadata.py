from lib import utils


class Metadata:
    def __init__(self, opcode, filename, filesize):
        self.opcode = opcode
        self.filename = filename
        self.filesize = filesize

    @classmethod
    def from_bytes(cls, message):
        opcode = message[0:1]
        filename = message[1:60].decode("utf-8").rstrip()
        filesize = int.from_bytes(message[60:], "big")
        return cls(opcode, filename, filesize)

    def is_upload(self):
        return self.opcode == utils.Command.UPLOAD.value

    def is_download(self):
        return self.opcode == utils.Command.DOWNLOAD.value

    def __bytes__(self):
        return (
            self.opcode
            + bytearray(f"{self.filename:59}", "utf-8")
            + self.filesize.to_bytes(4, "big")
        )

    def __str__(self):
        if self.is_download():
            return f"{utils.Command(self.opcode).name}: {self.filename}"
        return f"{utils.Command(self.opcode).name}: {self.filename} ({self.filesize} bytes)"
