import threading
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import msgpack
import socket

from . import MICROSERVICES, PASS_idx, IV_idx, MS_idx, SOCK_idx, UNSECURE_id
from .response import *
from .exception import *
from .default_client_handler import DefaultMicroserviceClient

# import time


class MicroserviceClient(DefaultMicroserviceClient):

    def __init__(self, client_socket, address, rsa_private_key, rsa_public_key, buffsize = 2048, **kwargs):
        super().__init__(rsa_private_key, buffsize)
        self.socket_client  = client_socket
        self.address = address
        self.rsa_public_key = rsa_public_key

    def start(self):
        self.rcv_from_client()
        if self.client_msg == "{{KEYPEMCODE}}".encode("UTF-8"):
            self._send(self.rsa_public_key, self.socket_client)
            return
        try:
            self._parse()
            self.open_ms_socket()
            self._decrypt_client_message()
            self._switch_socket()
        except NetworkException as e:
            response = ArchNetResponse()
            response.Exception_Raised(e.error_code, e.error_message)
            self.client_response =  msgpack.packb(response)
            self.send_to_client()
        except:
            response = ArchNetResponse()
            response.generic_error()
            self.client_response =  msgpack.packb(response)
            self.send_to_client()

    def _decrypt_ms(self):
        if MICROSERVICES[self.microservice].get("passphrase", None) is not None:
            aes = AES.new(MICROSERVICES[self.microservice]["passphrase"], AES.MODE_CFB, MICROSERVICES[self.microservice]["iv"])
            self.response_ms = aes.decrypt(self.ms_msg)

    def _encrypt_ms(self):
        if MICROSERVICES[self.microservice].get("passphrase", None) is not None:
            aes = AES.new(
                MICROSERVICES[self.microservice]["passphrase"],
                AES.MODE_CFB, MICROSERVICES[self.microservice]["iv"]
            )
            self.client_req = aes.decrypt(self.client_req)

    def _raise(self):
        raise Exception("Problem")

    def echo(self):
        self.client_response =  self.client_req
        self.send_to_client()

    def full_duplex(self):
        self.keep_open = True
        while self.keep_open:
            try:
                #self._decrypt_message()
                self._decrypt_client_message()
                self.send_to_ms()
                self.rcv_from_ms()
                self.send_to_client()
                self.rcv_from_client() # Fica no fim porque no start ja e lida a primeira
            except Exception as e:
                print(str(e))
                self.keep_open = False
        #self.close()
        self.send_to_client()

    def oneshot(self):
        self.close_client()
        self.send_to_ms()
        self.close_ms()

    def keepalive(self):
        self.send_to_ms()
        self.rcv_from_ms()
        self.send_to_client()

    def rcv_from_client(self):
        self.client_msg = self._rcv_from(self.socket_client)

    def rcv_from_ms(self):
        self.client_response = self._rcv_from(self.socket_ms)

    def _rcv_from(self, socket):
        msg = b''
        r = ""
        i = self.buffsize
        while i == self.buffsize and i > 0:
            r = socket.recv(self.buffsize)
            msg += r
            i = len(r)

        return msg

    def _send(self, msg, socket):
        socket.sendall(msg)

    def send_to_client(self):
        resp = self._encrypt_client_response()
        self._send(resp, self.socket_client)

    def send_to_ms(self):
        self._encrypt_ms()
        self._send(self.client_req, self.socket_ms)

    def close_client(self):
        self.socket_client.close()

    def close_ms(self):
        self.socket_ms.close()

    def test_me(self):
        self.end_time = time.time()
        import pymongo
        client = pymongo.MongoClient()
        client["ArchNetTests"]["ms_client_tests"].insert({
            "start" : self.start_time,
            "end"   : self.end_time,
            "response" : self.client_response,
            "microservice" : self.microservice
        })

    def __del__(self):
        #self.test_me() #RTL
        try:
            self.close_client()
            if self.socket_ms is not None:
                self.close_ms()
        except:
            pass
