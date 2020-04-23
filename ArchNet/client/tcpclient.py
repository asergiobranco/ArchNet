import socket
import sys


class Client(object):

    def __init__(self, port, hostname):
        self.port = port
        self.__buffsize = 2048

        try:
            self.hostname = socket.gethostbyname(hostname)
        except:
            raise Exception("BAD_GATEWAY")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.hostname, self.port))
        except:
            raise Exception("MICROSERVICE_UNREACHABLE")



    def __del__(self):
        try:
            if self.sock is not None:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
        except:
            pass

    def close(self):
        self.sock.close()
        self.sock = None

    def set_bufsize(self, bufsize):
        self.__buffsize = bufsize

    def __send(self, msg, bufsize = 2048):
        i = 0
        b = 0
        l = len(msg)
        text = b""
        while True:
            text +=msg[i:(i+self.__buffsize)]
            self.sock.send(msg[i:(i+self.__buffsize)])
            i+=(self.__buffsize)
            if (i+self.__buffsize) > l:
                text +=msg[i:]
                self.sock.send(msg[i:])
                break
        #self.sock.shutdown(socket.SHUT_WR)
        return text

    def send(self, msg):
        try:
            self.__send(msg)
        except Exception as e:
            print(e)

    def recv(self):
        BUFFSIZE =  self.__buffsize
        response  = b''
        r = ""
        i = BUFFSIZE
        while i == BUFFSIZE and i > 0:
            r = self.sock.recv(BUFFSIZE)
            response += r
            i = len(r)
        return response
