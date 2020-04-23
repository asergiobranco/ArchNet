import yaml
from Crypto.PublicKey import RSA
from Crypto import Random
from base64 import b64encode, b64decode
import threading
import socket

from ..default import MicroserviceClient
from ..default import MICROSERVICES
from . import StartMicroservices


from multiprocessing import Process

""" # TIME_TESTING
import time
import pymongo
#"""

#import cProfile
#from uuid import uuid4
def client_thread(client_socket, address, private_key, public_key):
    """ > #### `client_thread(client_socket, address, private_key, public_key)`
        >   Thread/Process to handle the client's request.
        >
        > __FlowChart__ :
        >   1. Creates `MicroserviceClient` instance.
        >   2. MicroserviceClient.start
        >   3. deletes the instance
        >
        > __Arguments__ :
        >   + *client_socket (socket)* : The socket where the client is connected to.
        >   + *address (ip)*
        >   + *private_key (RSA Key)* : The RSA key to decrypt the client's message
        >   + *public_key (RSA Key)*  : The RSA key to send if the client requests so.
        >
        > __Returns__ :
        > No return."""
    # start = time.time() #TIME_TESTING
    """
    uid = uuid4().hex
    cProfile.run("client = MicroserviceClient(client_socket, address, private_key, public_key)", "client_thread_profile_%s.txt" % (uid))
    cProfile.run("client.start()", "client_thread_profile_start_%s.txt" % (uid)
    # """
    client = MicroserviceClient(client_socket, address, private_key, public_key)
    client.start()
    # end = time.time() #TIME_TESTING
    """ #TIME_TESTING
    m_client = pymongo.MongoClient()
    m_client["ArchNet"]["time_tests"].insert({
        "type" : "Client Thread",
        "start" : start,
        "end"   : end,
        "microservice" : client.microservice,
        "socket"       : client.socket_type
    })
    m_client.close()
    # """
    del client
    return


class ArchNetServer(object):

    def __init__(self, config_file):
        """ > #### `__init__(self, config_file)`
            >   Creates a new ArchNet Server instance.
            >   This server can only attend raw TCP/IP comunications.
            >
            >   __FlowChart__:
            >   1. Opens the configure file and loads it into `self.configuration`.
            >   2. Calls `StartMicroservices` function, to create the global configuration variable `MICROSERVICES`.
            >   3. Configures the tcpserver socket and binds it.
            >
            >   __Arguments__:
            >   + *config_file (file_path)* : The path for the `YAML` configuration.
            >                                 The file should have the structure presented previously.
            >   __Returns__:
            >   + *ArchNetServer Object*. """
        with open(config_file) as fp:
            self.configuration = yaml.safe_load(fp)

        self.backlog = self.configuration["max_number"]

        StartMicroservices(config_file)

        self.tcpserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpserver.bind((
            self.configuration["hostname"],
            self.configuration["port"]
        ))


    def start(self):
        """ > #### `start(self)`
            >   Makes the server listen for new clients. The `backlog` is given by `self.backlog`.
            >   When a new client connects, a new client process is created.
            >
            > __FlowChart__ :
            >   1. Listens for upcomming connections.
            >   2. Call `self.client()` method to initiate a new process to attend the Client's request.
            >
            > __Arguments__ :
            >   No Argument is passed.
            >
            > __Returns__ :
            >   No return. The program gets stucked here."""
        self.tcpserver.listen(self.backlog)
        while True:
            self.client(
                self.tcpserver.accept(),
                self.configuration["RSA_PRIVATE_KEY"],
                self.configuration["RSA_PUBLIC_KEY"]
            )

    def client(self, client_tupple, private_key, public_key):
        """ > #### `client(self, client_tupple, private_key, public_key)`
            >   Initiates the Client's Process to attend its request. The target is the function `client_thread()`.
            >
            > __FlowChart__ :
            >   1. Gets the client socket and ip address.
            >   2. Starts the client's process with target `client_thread()`
            >
            > __Arguments__ :
            >   + *client_tupple (tupple)*        : Tupple containing socket,address.
            >   + *private_key (RSA PRIVATE KEY)* : The RSA private key to be used for decryption
            >   + *public_key (RSA PUBLIC KEY)*   : The RSA's public key. Currently not used.
            >
            > __Returns__ :
            >   No return. """
        client, client_add = client_tupple
        Process(target=client_thread, args=(client, client_add, private_key, public_key, )).start()
