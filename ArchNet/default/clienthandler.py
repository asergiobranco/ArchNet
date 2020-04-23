import msgpack
from functools import update_wrapper
from Crypto.Cipher import AES, PKCS1_OAEP
from .response import *
from .exception import *
from types import MethodType

def setupmethod(f):
    def wrapper_func(*args, **kwargs):
        return f(*args, **kwargs)

    return update_wrapper(wrapper_func, f)


class ArchNetClientHandler(object):

    def __init__(self, socket, address):
        """ > Initiallizes the client handler.
            >
            > Arguments:
            > * socket (socket.socket) : Socket object from python
            > * address (ip address) : Client's ip.
            >
            > Returns : No Return
            >."""
        self.socket = socket
        self.address = address
        self.buffsize = 2048
        self.response = ArchNetResponse()
        self.passphrase = None
        self.mode = AES.MODE_CFB
        self.IV = None


    def attendRequest(self, socket_type = "keep_alive"):
        """ > #### `attendRequest`
            > ```python
            >def attendRequest(self, socket_type = "keep_alive")
            >```
            >This method is responsible for handling the request, and call the function accordingly to the socket type passed.
            >Furthemore, this function checks if during the execution, a `NetworkException` is raised. If so, it sends the response to the user with the code and the message. If any exception is raised during the code execution a `GenericError` is sent as response.
            >
            > **Arguments**:
            > * __socket_type__ (string) : "keep_alive" | "one_shot" | "full_duplex"
            >
            > **Returns** : No Return
            >."""
        def switch(socket_type):
            return {
                "keep_alive" : lambda x : x._keep_alive(),
                "one_shot"   : lambda x : x._one_shot(),
                "full_duplex": lambda x : x._full_duplex()
            }.get(socket_type, None)

        try:
            switch(socket_type)(self)
        except NetworkException as e:
            self.response.Exception_Raised(e.error_code, e.error_message)
            self.send()
        except Exception as e:
            print(str(e))
            self.response.generic_error()
            self.send()
        # finally:
        #    self.send() # WARNING : Corrigir isto, na one shot não faz sentido

    def rcv_all(self):
        """ > #### `rcv_all`
            > ```python
            >def rcv_all(self)
            >```
            > Receives the entire message sent by the client.
            > The reception only stops when the length of the message is larger than the maximum size, or the socket in the client side was sundely closed.
            >
            > **Arguments**:
            >
            > **Returns** : No Return
            >."""
        self.msg = b''
        r = ""
        i = self.buffsize
        while i == self.buffsize and i > 0:
            r = self.socket.recv(self.buffsize)
            self.msg += r
            i = len(r)

    def close(self):
        self.socket.close()

    def send(self):
        self._encrypt_response()
        self._send(self.response)

    def _encrypt_response(self):
        if self.passphrase is not None:
            aes = AES.new(self.passphrase, self.mode, self.IV)
            self.response = aes.encrypt(self.response)
        self.response = msgpack.packb(self.response)

    def _decrypt_message(self):
        if self.passphrase is not None:
            aes = AES.new(self.passphrase, self.mode, self.IV)
            self.msg = aes.decrypt(self.msg)
        self.letter = msgpack.unpackb(self.msg, encoding = "utf-8")

    def _send(self, msg):
        self.socket.sendall(msg)

    def _keep_alive(self):
        self.rcv_all()
        self._decrypt_message()
        self.keep_alive_func()
        self.send()

    def _full_duplex(self):
        self.keep_open = True
        while self.keep_open:
            try:
                self.rcv_all()
                self._decrypt_message()
                self.full_duplex_func()
                self.send()
            except Exception as e:
                print(str(e))
                self.keep_open = False
        self.close()

    def _one_shot(self):
        self.rcv_all()
        self.close()
        self._decrypt_message()
        self.one_shot_func()

    def _check_for_keys(self):
        """Allows to check if all the keys are present in the letter. self.keys should be set."""
        keys_in_letter = set(self.letter.keys())
        if len(self.keys - keys_in_letter) != 0:
            raise BadRequest()

    def _op_not_found(self):
        raise OperationNotAllowed()


    """
    Decorators to describe the definition methods for each socket type.
    #"""

    def full_duplex_func(self):
        pass

    def keep_alive_func(self):
        pass

    def one_shot_func(self):
        pass

    @setupmethod
    def keep_alive(self, f):
        func= MethodType(f, self)
        object.__setattr__(self, 'keep_alive_func', func)
        return f

    @setupmethod
    def full_duplex(self, f):
        func= MethodType(f, self)
        object.__setattr__(self, 'full_duplex_func', func)
        return f

    @setupmethod
    def one_shot(self, f):
        func= MethodType(f, self)
        object.__setattr__(self, 'one_shot_func', func)
        return f
