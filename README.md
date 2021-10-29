# File transfer client and server

# Usage

## Start server

```
> cd src
> python start-server -h    
usage: start-server [-h] [-v {1,2,3}] [-q] [-H HOST] [-p PORT] [-P {udp,tcp,udp+saw,udp+gbn}] -s DEST

Parse flags for File Transfer App

optional arguments:
  -h, --help            show this help message and exit
  -v {1,2,3}, --verbose {1,2,3}
                        increase output verbosity
  -q, --quiet           decrease output verbosity
  -H HOST, --host HOST  server IP address
  -p PORT, --port PORT  server port
  -P {udp,tcp,udp+saw,udp+gbn}, --protocol {udp,tcp,udp+saw,udp+gbn}
                        protocol to use
  -s DEST, --storage DEST
                        storage dir path

```

## Start client

### Upload file

```
> cd src
> python upload-file -h
usage: upload-file [-h] [-v {1,2,3}] [-q] [-H HOST] [-p PORT] [-P {udp,tcp,udp+saw,udp+gbn}] -s SRC -n FILENAME

Parse flags for File Transfer App

optional arguments:
  -h, --help            show this help message and exit
  -v {1,2,3}, --verbose {1,2,3}
                        increase output verbosity
  -q, --quiet           decrease output verbosity
  -H HOST, --host HOST  server IP address
  -p PORT, --port PORT  server port
  -P {udp,tcp,udp+saw,udp+gbn}, --protocol {udp,tcp,udp+saw,udp+gbn}
                        protocol to use
  -s SRC, --src SRC     source file path
  -n FILENAME, --name FILENAME
                        file name
```

### Download file
```
> cd src
> python download-file -h
usage: download-file [-h] [-v {1,2,3}] [-q] [-H HOST] [-p PORT] [-P {udp,tcp,udp+saw,udp+gbn}] -d DST [-n FILENAME]

Parse flags for File Transfer App

optional arguments:
  -h, --help            show this help message and exit
  -v {1,2,3}, --verbose {1,2,3}
                        increase output verbosity
  -q, --quiet           decrease output verbosity
  -H HOST, --host HOST  server IP address
  -p PORT, --port PORT  server port
  -P {udp,tcp,udp+saw,udp+gbn}, --protocol {udp,tcp,udp+saw,udp+gbn}
                        protocol to use
  -d DST, --dst DST     Destination file path
  -n FILENAME, --name FILENAME
                        filename

```

## Run tests

Automated tests for running the server with the upload/download commands (tested on linux and macOS only). `-v` for printing full debug program output.

```
bash test-connection.sh <protocol> [-v]
```

To actually test the delivery guarantees, we need to simulate an unreliable or weak network. For this, we use [comcast](), a Go app. After installing `go` and `comcast`, you can run the same tests under our simulated environment with:

```
# We first need to know our network device, we can get it by grepping the lshw command
sudo lshw -C network | grep 'logical name' 
# In my case, my device is `enp2s0`

comcast --device=enp2s0 --packet-loss=10%
bash test-connection.sh <protocol> [-v]
comcast --stop
```