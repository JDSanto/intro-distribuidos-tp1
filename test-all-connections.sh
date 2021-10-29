#!/bin/bash

time ./test-connection.sh tcp
time ./test-connection.sh udp+gbn
time ./test-connection.sh udp+saw
