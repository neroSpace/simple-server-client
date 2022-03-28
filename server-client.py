#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter03/tcp_sixteen.py
# Simple TCP client and server that send and receive 16 octets

import argparse, socket
import sys
import time
import glob
# import string

def recvall(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('was expecting %d bytes but only received'
                           ' %d bytes before the socket closed'
                           % (length, len(data)))
        data += more
    return data

def server(interface, port):
    c = 0
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((interface, port))
        sock.listen(0)
        sc, sockname = sock.accept()
        print('Waiting to accept a new connection...')
        # sc, sockname = sock.accept()
        if c==0:
            print('We have accepted a connection from', sockname)
            c+=1
        print('Socket name:', sc.getsockname())
        print('Socket peer:', sc.getpeername())
        len_msg = recvall(sc, 3)
        message = recvall(sc, int(len_msg))
        acc_message = message.decode()
        str_message = acc_message.split()

        if str_message[0] == 'ping':
            # sc.sendall(message[1:])
            str_messageJoin = ' '.join(str_message[1:])
            # print('Terima:')
            print('Terima: ' + str_messageJoin)
            bit_message = str_messageJoin.encode()
            sc.sendall(bit_message)

        if str_message[0] == "ls":
            
            if len(str_message) == 1:
                files = '*'
            elif len(str_message) > 1:
                files = str_message[1]

            listed_files = glob.glob(files,recursive=True)
            return_files = ''
            
            for i in listed_files:
                return_files += i + '\n'
            print(return_files)
            len_ret_files = b"%03d" % (len(return_files))
            sc.sendall(len_ret_files)
            bit_return_files = return_files.encode()
            sc.sendall(bit_return_files)

        if str_message[0] == "get":
            listed_files = glob.glob(str_message[1])
            size = str(len(listed_files))
            return_message = "fetch:" + str_message[1] + " size:" + size + " lokal:" + str_message[2]
            print(return_message)
            bit_message = return_message.encode()
            sc.sendall(bit_message)
            print("Server shutdown..")
            time.sleep(1)
            print("Client shutdown..")
            sys.exit(0)

        if str_message[0] == "quit":
            print("Server shutdown..")
            time.sleep(1)
            print("Client shutdown..")
            sys.exit(0)

def client(host, port):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print('Client has been assigned socket name', sock.getsockname())
        input_msg = input("> ")
        msgSplit = input_msg.split()
       
        if msgSplit[0] == "ping":
            msgJoin = ' '.join(msgSplit)
            msg = msgJoin.encode()
            len_msg = b"%03d" % (len(msg),)
            msg = len_msg + msg
            sock.sendall(msg)
            reply = recvall(sock, len(msg)-8)
            reply1 = reply.decode()
            print(reply1)

        if msgSplit[0] == "ls":
            if len(msgSplit) == 1:
                msg = input_msg.encode()
                len_msg = b"%03d" % (len(msg),)
                msg = len_msg + msg
                sock.sendall(msg)
                len_recv = recvall(sock, 3)
                msg_recv = recvall(sock, int(len_recv))
                reply1 = msg_recv.decode()
                print(reply1)
            elif len(msgSplit) > 1:
                msgJoin = ' '.join(msgSplit)
                msg = msgJoin.encode()
                len_msg = b"%03d" % (len(msg),)
                msg = len_msg + msg
                sock.sendall(msg)
                len_recv = recvall(sock, 3)
                msg_recv = recvall(sock, int(len_recv))
                reply1 = msg_recv.decode()
                print(reply1)

        if msgSplit[0] == "get":
            msgJoin = ' '.join(msgSplit)
            msg = msgJoin.encode()
            len_msg = b"%03d" % (len(msg),)
            msg = len_msg + msg
            sock.sendall(msg)
            len_reply = recvall(sock,3)
            reply = recvall(sock, int(len_reply))
            reply1 = reply.decode()
            print(repr(reply1))
            print("Server shutdown..")
            time.sleep(2)
            print("Client shutdown..")
            sys.exit(0)

        if msgSplit[0] == "quit":
            msg = input_msg.encode()
            len_msg = b"%03d" % (len(msg),)
            msg = len_msg + msg
            sock.sendall(msg)
            print('Server shutdown...') 
            time.sleep(2)
            print('Client shutdown...')
            sys.exit(0)

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive over TCP')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('host', help='interface the server listens at;'
                        ' host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)
