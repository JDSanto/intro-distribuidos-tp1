import argparse
import logging
import os
from enum import Enum

DEFAULT_HOST = ''
DEFAULT_PORT = 8081
DEFAULT_SRC = './'
DEFAULT_DEST = 'lib/bucket'
VERBOSITY = {1: logging.DEBUG, 2: logging.INFO, 3: logging.ERROR}
INT_SIZE = 4
CHAR_SIZE = 1
MSJ_SIZE = 1024

class Command(Enum):
    UPLOAD = 'u'
    DOWNLOAD = 'd'


def parse_args():
    parser = argparse.ArgumentParser(description='Parse flags for File Transfer App')
    
    parser.add_argument(
        '-v', '--verbose', help='increase output verbosity', dest='verbose', type=int, choices=[1, 2, 3], default=1)
    parser.add_argument(
        '-q', '--quiet', help='decrease output verbosity', action='store_true')
    parser.add_argument(
        '-H', '--host', help='server IP address', dest='host', type=str, action='store')
    parser.add_argument(
        '-p', '--port', help='server port', dest='port', type=int, action='store')
    
    return parser
    
def parse_upload_file():
    parser = parse_args()
    parser.add_argument(
        '-s', '--src', help='source file path', dest='src', type=str, action='store', required=True, default=DEFAULT_SRC)
    parser.add_argument(
        '-n', '--name', help='file name', dest='filename', type=str, action='store', required=True)
    return validate_args(parser.parse_args())

def parse_download_file():
    parser = parse_args()
    parser.add_argument(
        '-d', '--dst', help='Destination file path', dest='dst', type=str, action='store', required=True)
    parser.add_argument(
        '-n', '--name', help='filename', dest='filename', type=str, action='store')
    return validate_args(parser.parse_args())

def parse_server_start():
    parser = parse_args()
    parser.add_argument(
        '-s', '--storage', help='storage dir path', dest='dest', type=str, action='store', required=True, default=DEFAULT_DEST)
    parser.add_argument('--name', dest='filename')
    return validate_args(parser.parse_args())

def validate_args(args):
    if args.verbose:
        args.verbose = level=VERBOSITY[args.verbose]
    if args.quiet:
        # TODO encontrar un NOSET que funque
        logging.basicConfig(level=logging.CRITICAL)
    if not args.host or not args.host.replace('.', '').isdigit():
        args.host = DEFAULT_HOST
    if args.port:
        if args.port < 1024 or args.port > 65535:
            args.port = DEFAULT_PORT
    if args.filename:
        # FIXME: this changes if the command is upload or download.
        # if not os.path.exists(args.filename):
        #     raise Exception(f'File {args.filename} not found')
        pass
    return args

def get_partitions(file_size):
    return file_size // MSJ_SIZE, file_size % MSJ_SIZE
            