import socket
import json
import base64

serverName = 'localhost'
serverPort = 12001

def load_file_to_base64(filename):
    with open(filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode('utf-8')

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
# sentence = input('Input the filename: ')

filename = input('Input filename: ')

# transform the content of the file to a base64 string
data = {
    'filename': filename,
    'data': load_file_to_base64(filename)
}
data_str = json.dumps(data).encode()
clientSocket.send(str(len(data_str)).encode())
clientSocket.send(json.dumps(data).encode())

# modifiedSentence = clientSocket.recv(1024)
# print('From Server: ', modifiedSentence.decode())
clientSocket.close()



