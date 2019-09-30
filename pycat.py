#! /usr/bin/python3
import sys
import socket
import threading
import subprocess
import argparse

listen = False
command = False
upload = False
execute = ""
target = ""
upload_dst = ""
port = 0

def main():
    global listen
    global port
    global execute
    global command
    global upload_dst

    # define args
    parser = argparse.ArgumentParser(description="Simple netcat clone")
    parser.add_argument("-p","--port", type=int, help="target port")
    parser.add_argument("-t", "--target_host", type=str, help="target host", default="0.0.0.0")
    parser.add_argument("-l", "--listen", help="listen on [host]:[port] for incomming connections", action="store_true", default=False)
    parser.add_argument("-e", "--execute", help="--execute=file_to_run execute the given file upn receiving a connection")
    parser.add_argument("-c", "--command", help="initialize a command shell",action="store_true", default=False)
    parser.add_argument("-u", "--upload", help="--upload=destination upon receing connection upload a file and write to [destination]")
    args = parser.parse_args()

    # parse args
    port = args.port
    target = args.target_host
    listen = args.listen
    execute = args.execute
    command = args.command
    upload_dst = args.upload

    # are we going to listen or just send data from stdin?
    if not listen and target is not None and port > 0:
        print("DBG: read data from stdin")
        buffer = sys.stdin.read()  # read from stdin, this will block so send CTRL-D if not sending to stdin

        print(f"Sending {buffer} to client")
        client_sender(buffer)  # send data

    # we are going to listen and potentially upload things, execute
    # commands and drop a shell back, depending on the command line options
    if listen:
        server_loop()


def server_loop():
    global target

    print("DBG: entering server loop")

    # if target not defined, listen on all interfaces
    if not target:
        target = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # create a thread to handle new client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def client_handler(client_socket):
    global upload
    global execute
    global command

    print("DBG: handling client socket")

    if upload_dst: # check for upload
        print("DBG: entering file upload")

        file_buffer = ""

        while True: # read in data and output to destination
            data = client_socket.recv(1024)
            if not data: # keep reading data till None
                break
            else:
                file_buffer += data.decode()

        # now take data and try to output
        try:
            file_descriptor = open(upload_dst, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # acknowledge output
            client_socket.send(f"Successfully saved file to {upload_dst}\r\n".encode())

        except:
            client_socket.send(f"Failed to save file to {upload_dst}\r\n").encode()

    if execute: # check for command execution
        print("DBG: going to execute command")

        output = run_command(execute) # run command and get output
        client_socket.send(output.encode()) # send output

    if command:
        print("DBG: shell requested")
        client_socket.send("<PYCAT:#> ".encode()) # show a simple prompt
        while True:
            # now recieve until linefeed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            response = run_command(cmd_buffer) # run command and get response

            # check if response is string, encode if so
            if isinstance(response, str):
                response = response.encode()

            client_socket.send(response + "<PYCAT:#> ".encode()) # send back response


def run_command(command):
    command = command.rstrip() # trim any '\n'

    print("DBG: executing command: " + command)

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True) # execute shell command and pass output
    except:
        output = "failed to execute command.\r\n"

    return output


def client_sender(buffer):
    print("DBG: sending data to client on port " + str(port))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target,port)) # connect to target

        if buffer:
            client.send(buffer.encode())
        while True:
            # wait for data
            recv_len = 1
            response = ""

            while recv_len:
                print("DBG: waiting for response from client")
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()
                # response = ''.join(data)

                if recv_len < 4096:
                    break

            print(response, end="")

            buffer = input() # wait for more input
            buffer += '\n'

            client.send(buffer.encode()) # send input

    except:
        print("[*] Exception! Exiting.")
    finally:
        client.close()  # close connection


main()
