import socket
import json
import base64
import os

DEST_FOLDER = 'bucket'

def write_base64_string_to_file(data, filename):
    with open(os.path.join(DEST_FOLDER, filename), 'wb') as f:
        f.write(base64.b64decode(data))


serverPort = 12001
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready to receive')
while True:
    connectionSocket, addr = serverSocket.accept()
    data_len = int(connectionSocket.recv(1024).decode())
    print(data_len)
    data = connectionSocket.recv(10240000000).decode()
    data = json.loads(data)
    write_base64_string_to_file(data['data'], data['filename'])
    # capitalizedSentence = sentence.upper()
    # connectionSocket.send(capitalizedSentence.encode())
    # connectionSocket.close()

