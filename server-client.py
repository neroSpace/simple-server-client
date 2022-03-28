#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter03/tcp_sixteen.py
# Simple TCP client and server that send and receive 16 octets

import argparse, socket
import sys
import time
import glob
import os
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
        sock.listen(1)
        sc, sockname = sock.accept()
        if c==0:
            print('Waiting to accept a new connection...')
            print('We have accepted a connection from', sockname)
            c+=1
        print('Socket name:', sc.getsockname())
        print('Socket peer:', sc.getpeername())
        len_msg = recvall(sc, 3)
        message = recvall(sc, int(len_msg))

        #Decode and split the message from client
        acc_message = message.decode()
        str_message = acc_message.split()

        #Condition for ping command
        if str_message[0] == 'ping':
            str_messageJoin = ' '.join(str_message[1:])
            format1 = "terima: "
            bit_message = format1.encode() + str_messageJoin.encode()
            len_bit_message = b"%03d" % (len(bit_message.decode()),)
            sc.sendall(len_bit_message)
            sc.sendall(bit_message)

        #Condition to follow for ls command
        elif str_message[0] == "ls":
            #Condition to follow for ls-only
            if len(str_message) == 1:
                files = '*'
            #Condition to follow for ls with follow-up path
            elif len(str_message) > 1:
                files = str_message[1]

            listed_files = glob.glob(files,recursive=True)
            return_files = ''
            for i in listed_files:
                basename = os.path.basename(i)
                return_files += basename + '\n'
            len_ret_files = b"%03d" % (len(return_files))
            sc.sendall(len_ret_files)
            bit_return_files = return_files.encode()
            sc.sendall(bit_return_files)

        #Condition to follow for get command
        elif str_message[0] == "get":
            #Assign the path input to variable p
            p = os.path.dirname(str_message[1])
            #Assign the filename input to variable names
            names = str_message[2]
            #Initiate variable for length counter
            sizes = 0
            #Search the file in the path directory p
            for files in os.scandir(p):
                basename = os.path.basename(files)
                if basename.startswith(str_message[2]):
                    #Open, read and count the length of the files
                    f = open(files,"rb")
                    b = f.read()
                    sizes += len(b)
                    f.close()
            size = str(sizes)
            space =" "
            format1 = "fetch: "
            format2 = "size: "
            format3 = "lokal: "
            #Encode the return messsage for client
            return_message = format1.encode() + p.encode() + space.encode() + format2.encode() + size.encode() + space.encode() + format3.encode() + names.encode()
            len_ret_message = b"%03d" % (len(return_message.decode()),)
            sc.sendall(len_ret_message)
            sc.sendall(return_message)
        #Condition to follow for quit command
        elif str_message[0] == "quit":
            print("Server shutdown..")
            sc.close()
            sys.exit(0)

def client(host, port):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print('Client has been assigned socket name', sock.getsockname())
        #Input and split message
        input_msg = input("> ")
        msgSplit = input_msg.split()
       
        #Condition to follow for if command
        if msgSplit[0] == "ping":
            msgJoin = ' '.join(msgSplit)
            msg = msgJoin.encode()
            len_msg = b"%03d" % (len(msg),)
            msg = len_msg + msg
            sock.sendall(msg)
            len_recv = recvall(sock, 3)
            msg_recv = recvall(sock, int(len_recv))
            reply1 = msg_recv.decode()
            print(reply1)

        #Condition to follow for ls command
        elif msgSplit[0] == "ls":
            #Condition to follow for ls-only
            if len(msgSplit) == 1:
                msg = input_msg.encode()
                len_msg = b"%03d" % (len(msg),)
                msg = len_msg + msg
                sock.sendall(msg)
                len_recv = recvall(sock, 3)
                msg_recv = recvall(sock, int(len_recv))
                reply1 = msg_recv.decode()
                print(reply1)

            #Condition to follow for ls with follow-up path
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

        #Condition to follow for get command
        elif msgSplit[0] == "get":
            msgJoin = ' '.join(msgSplit)
            msg = msgJoin.encode()
            len_msg = b"%03d" % (len(msg),)
            msg = len_msg + msg
            sock.sendall(msg)
            len_recv = recvall(sock, 3)
            msg_recv = recvall(sock, int(len_recv))
            reply1 = msg_recv.decode()
            print(reply1)

        #Condition to follow for quit command
        elif msgSplit[0] == "quit":
            msg = input_msg.encode()
            len_msg = b"%03d" % (len(msg),)
            msg = len_msg + msg
            sock.sendall(msg) 
            time.sleep(2)
            print('Client shutdown...')
            sock.close()
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
