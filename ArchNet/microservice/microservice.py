import socket
import threading
from ..default import ArchNetClientHandler
from functools import update_wrapper
from multiprocessing import Process

def setupmethod(f):
    def wrapper_func(self, *args, **kwargs):
        return f(self, *args, **kwargs)

    return update_wrapper(wrapper_func, f)

class Microservice(object):
    """This class implements a Microservice.  To implement the proper microservice, use the following nomenclature:
        ```python
        class MyMicroservice(Microservice):
	           def __init__(self, *args, **kwargs):
		                 super().__init__( *args, **kwargs)
        ```
    """
    def __init__(self, port, hostname, microservicename, backlog = 100):
        self.microservice_name = microservicename
        self.port = port
        self.hostname = hostname
        self.backlog = backlog
        self.tcpserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpserver.bind((
            self.hostname,
            self.port
        ))


    def start(self):
        self.tcpserver.listen(self.backlog)
        while True:
            self.client(
                self.tcpserver.accept()
            )

    def client(self, client_tupple):
        client, client_add = client_tupple
        Process(target=self.ClientThread, args=(client, client_add,)).start()

    @setupmethod
    def client_thread(self, f):
        self.ClientThread = f
        return f
