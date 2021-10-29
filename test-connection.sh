#!/bin/bash

TEST_FILE=test.txt
TEST_BUCKET_NAME=test-bucket

STD_REDDIR='/dev/null'

SERVER_PID=0
ERROR=0

clean_testing_files() {
    rm -r -f $TEST_BUCKET_NAME
    rm -f $TEST_FILE
}

start_server() {
    # starts the server, sets the server PID
    python src/start-server -P $1 -s $TEST_BUCKET_NAME >"$STD_REDDIR" 2>&1 &
    SERVER_PID=$!
    sleep 0.2
}

stop_server() {
    # stops the server, sets the server PID to 0
    kill $SERVER_PID
    SERVER_PID=0
}


check_server_status() {
    # exits the program if the last background job exited
    # regardless of status code

    kill -0 "$SERVER_PID"
    if [ $? -ne 0 ]; then
        echo "ERROR: Server exited unexpectedly"
        exit 1
    fi
}

generate_file() {
    # generates a file with $1 characters
    if [ $1 -lt 1000 ]; then
    	head -c $1 /dev/urandom > $TEST_FILE
    else
		dd if=/dev/urandom of=$TEST_FILE bs=1000 count=$(($1 / 1000)) 2> /dev/null
	fi 
}

client_transfer_file() {
    cmd="python src/$1-file -P $2 -$3 . -n $TEST_FILE"
	
	local start=$(date +%s%N)
    $cmd > "$STD_REDDIR" 2>&1 &
    wait $!
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: Client exited unexpectedly"
        ERROR=1
    fi
    
	ELAPSED=$(echo "print(($(date +%s%N) - ${start})/1000000000.0)" | python)
	echo >> "${RESULTS:-/dev/null}" "${PLOSS};${SIZE};${PROTO};${1};${ELAPSED};${exit_code}"
    
    diff $TEST_FILE $TEST_BUCKET_NAME/$TEST_FILE >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "ERROR: Files differ."
        ERROR=1
    fi
    sleep 0.1
}

client_upload_file() {
    client_transfer_file upload $1 "s"
}

client_download_file() {
    client_transfer_file download $1 "d"
}

kill_system() {
    jobs -p | xargs kill -9 >/dev/null 2>&1
}


test_system() {
    # test system
    # args: <PROTOCOL> <file size in bytes>

    printf "Testing $1 with a random file of $2 bytes... "

    clean_testing_files

    check_server_status

    generate_file $2

    PROTO=$1 SIZE=$2 client_upload_file $1

    check_server_status

    PROTO=$1 SIZE=$2 client_download_file $1

    check_server_status

    clean_testing_files

    if [ $ERROR -eq 0 ]; then
        echo "OK"
    else
        echo "FAIL"
        return 1
    fi
}

trap kill_system SIGINT


if [ "$#" == 0 ]; then
    echo "Invalid parameter count"
    echo "Usage: ./test-connection.sh <PROTOCOL> [-v]"
    exit 1
fi

if [ "$2" == '-v' ]; then
    STD_REDDIR='/dev/tty'
fi

start_server $1

for i in 100 1000 10000 100000 1000000; do
    test_system $1 $i
    sleep 0.25
    if [ $ERROR -ne 0 ]; then
        break
    fi
done

stop_server

kill_system

if [ $ERROR -ne 0 ]; then
    exit 1
else
    exit 0
fi

