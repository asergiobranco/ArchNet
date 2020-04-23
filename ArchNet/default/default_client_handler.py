"""The following Class in responsible for implementing the default behaviour across servers."""
import threading
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import msgpack
import socket

from . import MICROSERVICES, PASS_idx, IV_idx, MS_idx, SOCK_idx, UNSECURE_id
from .response import *
from .exception import *

        
class DefaultMicroserviceClient(object):

    def __init__(self, rsa_private_key, buffsize):
        self.rsa_private_key = rsa_private_key
        self.key = RSA.importKey(self.rsa_private_key)
        self.decryptor = PKCS1_OAEP.new(self.key)
        self.buffsize = buffsize
        self.socket_type = ""
        self.socket_ms = None
        self.client_response = b''
        self.microservice = None
        self.client_pass = None
        self.client_IV = None
        self.client_msg = None
    
    def _switch_socket(self):
        def switch(socket_type):
            return {
                '0' : lambda x : x.keepalive(), #Keep-alive Soket
                '1' : lambda x : x.oneshot(),
                '2' : lambda x : x.full_duplex(),
                '3' : lambda x : x.echo()
            }.get(socket_type, lambda x : x.close())

        if isinstance(self.socket_type, bytes):
            self.socket_type = self.socket_type.decode("utf-8")

        switch(self.socket_type)(self)
    
    def open_ms_socket(self):
        try:
            hostname= socket.gethostbyname(MICROSERVICES[self.microservice]["hostname"])
            self.socket_ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_ms.connect((hostname, MICROSERVICES[self.microservice]["port"]))
        except:
            raise NotFound()
    
    def _parse(self):
        """Parses the STAMP. Raises RSAKeyFailed if cannot unpack or decrypt the client's letter."""
        try:
            stamps = msgpack.unpackb(self.decryptor.decrypt(self.client_msg[:128]))
            self.microservice = stamps[MS_idx].decode("UTF-8")
            self.socket_type = stamps[SOCK_idx]
            if len(self.client_msg) == 128 and self.socket_type == b'1':
                self.client_msg = msgpack.unpackb(stamps[UNSECURE_id])
            else:
                self.client_pass = stamps[PASS_idx]
                self.client_IV = stamps[IV_idx]
                self.client_msg = self.client_msg[128:]
                if len(self.client_msg) == 0:
                    raise Exception("No Len")
        except Exception as e:
            print(e)
            raise RSAKeyFailed()
    
    def _pad(self, data):
        length = 16 - (len(data) % 16)
        return data + (chr(length)*length).encode()

    def _unpad(self, data):
        j = 0
        lc = data[-1]
        for i in range(-1, -len(data), -1):
            if data[i] != lc:
                j = i
                break
        return data[:j+1]
    
    def _decrypt_client_message(self):
        if self.client_pass != None and self.client_IV != None:
            aes = AES.new(self.client_pass, AES.MODE_CBC, self.client_IV)
            self.client_req  = self._unpad(aes.decrypt(self.client_msg ))
        else:
            self.client_req  = self.client_msg
            
    def _encrypt_client_response(self):
        aes = AES.new(self.client_pass, AES.MODE_CBC, self.client_IV)
        return aes.encrypt(self._pad(self.client_response))
