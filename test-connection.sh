#!/bin/bash

TEST_FILE=test.txt
TEST_BUCKET_NAME=test-bucket
TEST_FILE_CHECKSUM=""

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
    sleep 0.1
}

stop_server() {
    # stops the server, sets the server PID to 0
    kill $SERVER_PID
    SERVER_PID=0
}

get_checksum() {
    # gets the checksum of the file
    echo $(sha256sum $1 | cut -d ' ' -f 1)
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
    # and stores its checksum 

    # generate file
    head -c $1 /dev/urandom > $TEST_FILE

    # get checksum and store it to the variable TEST_FILE_CHECKSUM
    TEST_FILE_CHECKSUM=$(get_checksum $TEST_FILE)
}

client_upload_file() {
    python src/upload-file -P $1 -s . -n $TEST_FILE >"$STD_REDDIR" 2>&1
    if [ $? -ne 0 ]; then
        echo "ERROR: Client exited unexpectedly"
        ERROR=1
    fi

    RESULT_CHECKSUM=$(get_checksum $TEST_BUCKET_NAME/$TEST_FILE)

    if [ $TEST_FILE_CHECKSUM != $RESULT_CHECKSUM ]; then
        echo "ERROR: Checksum mismatch"
        ERROR=1
    fi
}

client_download_file() {
    python src/download-file -P $1 -d . -n $TEST_FILE >"$STD_REDDIR" 2>&1
    if [ $? -ne 0 ]; then
        echo "ERROR: Client exited unexpectedly"
    fi

    RESULT_CHECKSUM=$(get_checksum $TEST_FILE)

    if [ $TEST_FILE_CHECKSUM != $RESULT_CHECKSUM ]; then
        echo "ERROR: Checksum mismatch."
    fi
}


test_system() {
    # test system
    # args: <PROTOCOL> <file size in bytes>

    printf "Testing $1 with a random file of $2 bytes... "

    clean_testing_files

    start_server $1

    check_server_status

    generate_file $2

    client_upload_file $1

    check_server_status

    client_download_file $1

    check_server_status

    stop_server

    clean_testing_files

    if [ $ERROR -eq 0 ]; then
        echo "OK"
    else
        echo "FAIL"
        exit 1
    fi
}


if [ "$#" == 0 ]; then
    echo "Invalid parameter count"
    echo "Usage: ./test-connection.sh <PROTOCOL> [-v]"
    exit 1
fi

if [ "$2" == '-v' ]; then
    STD_REDDIR='/dev/tty'
fi

for i in 100 1000 10000 100000 1000000 10000000 50000000; do
    test_system $1 $i
    sleep 0.25
done
