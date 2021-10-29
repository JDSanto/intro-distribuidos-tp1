import argparse
import logging
from enum import Enum

DEFAULT_HOST = ""
DEFAULT_PORT = 8081
DEFAULT_SRC = "./"
DEFAULT_DEST = "lib/bucket"
VERBOSITY = {1: logging.DEBUG, 2: logging.INFO, 3: logging.ERROR}
INT_SIZE = 4
CHAR_SIZE = 1
MSG_SIZE = 1024
MAX_DG_SIZE = (1 << 16) - 1
METADATA_FIXED_SIZE = 64


class Command(Enum):
    UPLOAD = b"u"
    DOWNLOAD = b"d"
    SHUTDOWN = b"s"


class Status(Enum):
    OK = b"o"
    ERROR = b"e"


class Protocol(Enum):
    UDP = "udp"
    TCP = "tcp"
    SAW = "udp+saw"
    GBN = "udp+gbn"

    def __str__(self):
        return self.value


def parse_args():
    parser = argparse.ArgumentParser(description="Parse flags for File Transfer App")

    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        dest="verbose",
        type=int,
        choices=[1, 2, 3],
        default=1,
    )
    parser.add_argument(
        "-q", "--quiet", help="decrease output verbosity", action="store_true"
    )
    parser.add_argument(
        "-H", "--host", help="server IP address", dest="host", type=str, action="store"
    )
    parser.add_argument(
        "-p",
        "--port",
        help="server port",
        dest="port",
        type=int,
        action="store",
        default=DEFAULT_PORT,
    )
    parser.add_argument(
        "-P",
        "--protocol",
        help="protocol to use",
        dest="protocol",
        type=Protocol,
        choices=list(Protocol),
        default=Protocol.TCP,
    )

    return parser


def parse_upload_file():
    parser = parse_args()
    parser.add_argument(
        "-s",
        "--src",
        help="source file path",
        dest="src",
        type=str,
        action="store",
        required=True,
        default=DEFAULT_SRC,
    )
    parser.add_argument(
        "-n",
        "--name",
        help="file name",
        dest="filename",
        type=str,
        action="store",
        required=True,
    )
    return validate_args(parser.parse_args())


def parse_download_file():
    parser = parse_args()
    parser.add_argument(
        "-d",
        "--dst",
        help="Destination file path",
        dest="dst",
        type=str,
        action="store",
        required=True,
    )
    parser.add_argument(
        "-n", "--name", help="filename", dest="filename", type=str, action="store"
    )
    return validate_args(parser.parse_args())


def parse_server_start():
    parser = parse_args()
    parser.add_argument(
        "-s",
        "--storage",
        help="storage dir path",
        dest="dest",
        type=str,
        action="store",
        required=True,
        default=DEFAULT_DEST,
    )
    return validate_args(parser.parse_args())


def validate_args(args):
    if args.verbose:
        args.verbose = VERBOSITY[args.verbose]
    if args.quiet:
        logging.disable(level=logging.CRITICAL + 1)
    if not args.host or not args.host.replace(".", "").isdigit():
        args.host = DEFAULT_HOST
    if args.port:
        if args.port < 1024 or args.port > 65535:
            args.port = DEFAULT_PORT
    return args
