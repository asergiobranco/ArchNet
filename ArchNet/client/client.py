from .tcpclient import Client

import yaml
from Crypto.PublicKey import RSA
import msgpack
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_OAEP
import base64

from ..default import PASS_idx, IV_idx, MS_idx, SOCK_idx, UNSECURE_id

BLOCK_SIZE=16
PASS_SIZE = 32

class ArchNetClient(object):

    def __init__(self, port, hostname, secure = True):
        """ > #### `__init__(self, port, hostname, secure = True)`
            >
            >   Creates an instance able to communicate with an `ArchNetServer`.
            >
            > __Arguments__:
            >   + port (int)
            >   ....: The port where the ArchNetServer expects to receive a connection.
            >   + hostname (str)
            >   ....: The hostname the ArchNetServer is hosted.
            >   + secure (boolean, default = True)
            >   ....: Should be set to `false` if you intend to use one-shot socket.
            >
            > __Attributes__ :
            >   + port (int)
            >   ....: The server's port number.
            >   + hostname (str)
            >   ....: The server's hostname.
            >   + raw_stamp (list)
            >   ....: The stamp before being encrypted or serialized.
            >   + \_pass_idx (int)
            >   ....: The stamp list index where the AES passphrase will be sent.
            >   + \_iv_idx (int)
            >   ....: The stamp list index where the AES iv will be sent.
            >   + \_msname_idx (int)
            >   ....: The stamp list index where the microservice name will be sent.
            >   + \_socket_idx (int)
            >   ....: The stamp list index where the socket type will be sent.
            >   + \_unsecure_idx (int)
            >   ....: The stamp list index where the letter is sent in case of unsercure method.
            >   + socket_type (numeric char)
            >   ....: The socket's type
            >   + c (tcpclient object)
            >   ....: The raw tcp/ip client instance.
            >
            >  __Attributes in Run Time__:
            >   + stamp
            >   + letter
            >   + passphrase
            >   + IV
            >   + microservicename
            >   + rsa_key
            >   + enc
            >   + key
            >   + response
            >
            > __Returns__:
            >   ArchNetClient instance
            > ."""
        self.port = port
        self.hostname = hostname
        self.raw_stamp = [None, None, None, None]
        self._pass_idx = PASS_idx
        self._iv_idx = IV_idx
        self._msname_idx = MS_idx
        self._socket_idx = SOCK_idx
        self._unsecure_idx = UNSECURE_id
        self._secure = secure
        self.set_socket_type("keep-alive")
        self.c = None

    def send(self, message, microservicename):
        """ > #### `send(self, message, microservicename)`
            >
            >   This method is responsible to send the message to the given microservice.
            >
            > __Arguments__:
            >   + message (object)
            >   ....: Unserialized object (int, list, string...) to be sent to the microservice. The message should follow the format expected by the Microservice.
            >   + microservicename (string)
            >   ....: The microservice's name inside the server.
            >
            > __FlowChart__:
            > 1. Packs the message
            > 2. sets the microservice name
            > 3. sets the AES credentials (if not secure)
            > 4. Encrypts the stamp
            > 5. Encrypts the letter
            > 6. Calls `self._switch_socket`
            >
            > __Returns__:
            >  No return.
            >."""
        if not isinstance(message, bytes):
            message = msgpack.packb(message)


        self._set_microservicename(microservicename)

        if self._secure:
            self._set_pass()
            self._set_iv()
        else:
            self._set_unsecure_message(message)


        self.stamp = self.enc.encrypt(self._stamp())


        self.letter =  self.stamp

        if self._secure:
            self.letter = self.letter + self._encrypt(message)

        self._switch_socket()(self)

    def _switch_socket(self):
        def _raise():
            print("Key Not Found")
        a = {
            '0' : lambda x : x._keep_alive(),
            '1' : lambda x : x._one_shot(),
            '2' : lambda x : x._full_duplex(),
            '3' : lambda x : x._keep_alive()
        }
        return a.get(self.socket_type, lambda x : x.close() )

    def _set_unsecure_message(self, message):
        self.set_socket_type("one-shot")
        self.raw_stamp[self._unsecure_idx] = msgpack.packb(message)

    def _send(self, message):
        if self.c is None:
            self.c = Client(self.port, self.hostname)
        self.c.send(message)

    def _recv(self):
        return self.c.recv()

    def _stamp(self):
        return msgpack.packb(self.raw_stamp)

    def set_socket_type(self, _type):
        def switch(_type):
            return {
                "keep-alive"  : '0',
                "one-shot"    : '1',
                "full-duplex" : '2',
                "echo"        : '3'
            }.get(_type, '0')

        self.socket_type = switch(_type)
        self.raw_stamp[self._socket_idx] = self.socket_type


    def _set_pass(self):
        self.passphrase = Random.new().read(PASS_SIZE)
        self.raw_stamp[self._pass_idx] = self.passphrase

    def _set_iv(self):
        self.IV = Random.new().read(BLOCK_SIZE)
        self.raw_stamp[self._iv_idx] = self.IV

    def _set_microservicename(self, microservicename):
        _max_len = 16
        if len(microservicename.encode("utf-8")) <= _max_len:
            self.microservicename = microservicename.encode("utf-8")
            self.raw_stamp[self._msname_idx] = self.microservicename
        else:
            raise Exception("The Microsevice name, must be up to %s bytes" % (_max_len))

    def _fd_func(self):
        self.letter = self.response
        if self.empty == 5:
            self.keep_open = False
        self.empty += 1

    def _full_duplex(self):
        self.keep_open = True
        while self.keep_open:
            try:
                self._send(self.letter)
                self.response = self._recv()
                self._fd_func()
            except Exception as e:
                print(str(e))
                self.keep_open = False
        self.close()

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

    def _decrypt(self):
        aes = AES.new(self.passphrase, AES.MODE_CBC, self.IV)
        return self._unpad(aes.decrypt(self.response))

    def _encrypt(self, message):
        aes = AES.new(self.passphrase, AES.MODE_CBC, self.IV)
        return aes.encrypt(self._pad(message))

    def _keep_alive(self):
        self._send(self.letter)

        self.response = self._recv()

        self.response = msgpack.unpackb(self._decrypt(), encoding = "utf-8")

        self.close()

    def _one_shot(self):
        self._send(self.letter)
        self.close()

    def set_key(self, rsa_key):
        """ > #### `set_key(self, rsa_key)`
            >   Sets the Public RSA Key to be used in the stamps encryption. Should be called if you already have the key.
            >
            > __Arguments__:
            >   + rsa_key
            >   ....: The RSA Public Key String.
            >
            > __Attributes__:
            >   + rsa_key
            >   ....: The RSA Key in a string format.
            >   + key
            >   ....: The RSA Key obtained from calling `RSA.importKey`.
            >   + enc
            >   ....: And instance of `PKCS1_OAEP.new`.
            >
            > __FlowChart__:
            >   1. Copies the rsa_key to the attribut `rsa_key`.
            >   2. Calls `RSA.importKey`.
            >   3. Creates the encrypter instance.
            >
            > __Returns__:
            >   No Return.
            >  . """
        self.rsa_key = rsa_key
        self.key =RSA.importKey(self.rsa_key)
        self.enc = PKCS1_OAEP.new(self.key)

    def get_rsa_key(self, code = "KEYPEMCODE"):
        """ > #### `get_rsa_key(self, code = "KEYPEMCODE")`
            >   Method to automatically asks the server for its Public RSA Key (if the server allows to). Otherwise, you have to set it using `set_key`.
            >
            > __Arguments__:
            >   + code (str)
            >   ....: The string used to make the request. The server can change it, but by default is "KEYPEMCODE". Note, the function adds a `{{` and a `}}` to the string.
            >
            > __FlowChart__:
            >   1. Sets the correct code
            >   2. Calls `_send` method.
            >   3. Waits to receive the key.
            >   4. Sets the RSA Key.
            >   5. Closes the connection.
            >
            > __Returns__:
            >   True/False """

        ret = True
        self.letter = ("{{%s}}" % (code)).encode("UTF-8")
        self._send(self.letter)

        try:
            rsa_key = self._recv()
            self.set_key(rsa_key)
        except:
            ret = False
        finally:
            self.close()

        return ret

    def close(self):
        self.c.close()
        self.c = None
