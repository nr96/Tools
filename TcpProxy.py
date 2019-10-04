#!/usr/bin/python3
import sys, socket, threading, argparse

def receive_from(connection):
    buffer = ""
    # set a 2 sec timeout
    # may be adjusted according to target
    connection.settimeout(2)

    try:
        # keep reeading buffer until no data or timeout
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass

    return buffer

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = b''.join(["%0*X".encode() % (digits, ord(x)) for x in s])
        hexa = b' '.join(["%0*X".encode() % (digits, ord(x)) for x in s])
        text = b''.join([x.encode() if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text))

    print(b'\n'.join(result))


def response_handler(buffer):
    # perform the necessary packet modifications
    return buffer

def request_handler(buff):
    # perform the necesary packet modifications
    return buff

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print(f"[!!] Failed to listen in {local_host}:{local_port}")
        print("[!!] Check for other listening sockets or correct permissons.")
        sys.exit(0)

    print("[*] Listening on {local_host}:{local_port}")
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print(f"[==>] Received incoming connection from {addr[0]}:{addr[1]}")

        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    parser = argparse.ArgumentParser(description="A simple TCP proxy tool")
    parser.add_argument("local_host", type=str, help="host IP")
    parser.add_argument("local_port", type=int, help="host port")
    parser.add_argument("remote_host", type=str, help="remote host IP")
    parser.add_argument("remote_port", type=int, help="remote host port")
    parser.add_argument("receive_first", type=str, help="should we receive first? [True/False]")
    args = parser.parse_args()

    receive_first = True if "True" in args.receive_first else False

    # start server
    server_loop(args.local_host, args.local_port, args.remote_host, args.remote_port, receive_first)

def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))

    # receieve data from remote if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)

        # if there is data to send to the local client, do it
        if remote_buffer:
            print(f"[<==] Sending {len(remote_buffer)} bytes to local_host")
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket) # read from local host

        if local_buffer:
            print(f"[==>] Received {len(local_buffer)} bytes from local_host")
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer) # send to request handler
            remote_socket.send(local_buffer) # send off the data to the remote host
            print("[==>] Sent to remote")

        remote_buffer = receive_from(remote_socket)

        if remote_buffer:
            print(f"[<==] Received {len(remote_buffer)} bytes to remote")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer) # send to response_handler
            client_socket.send(remote_buffer) # send response to local socket
            print("[==>] Sent to localhost")

        # if no more data on either side, close the connections
        if not local_buffer or not remote_buffer:
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


main()
