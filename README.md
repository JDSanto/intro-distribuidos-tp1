
# Usage

> TODO: Sacado del enunciado. Cambiarlo también en el programa y actualizarlo acá.

## Start server

```
> cd src
> python start-server -h
usage: start-server [- h] [- v | -q] [- H ADDR] [- p PORT] [- s DIRPATH]

optional arguments:
-h, -- help     show this help message and exit
-v, -- verbose  increase output verbosity
-q, -- quiet    decrease output verbosity
-H, -- host     service IP address
-p, -- port     service port
-s, --storage   storage dir path
```

## Start client

### Upload file

```
> cd src
> python upload-file -h
usage: file-upload [-h] [-v | -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]

-h, --help      show this help message and exit
-v, --verbose   increase output verbosity
-q, --quiet     decrease output verbosity
-H, --host      server IP address
-p, --port      server port
-s, --src       source file path
-n, --name      file name
```

### Download file
```
> cd src
> python download-file -h
usage: download-file [-h] [-v | -q] [-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME]

-h, --help      show this help message and exit
-v, --verbose   increase output verbosity
-q, --quiet     decrease output verbosity
-H, --host      server IP address
-p, --port      server port
-d, --dst       destination file path
-n, --name      file name
```
