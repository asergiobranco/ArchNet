class empty_class(dict):
    def __init__(self):
        super().__init__()

    def __setitem__(self, key, value):
        if key in self:
            raise Exception("Immutable")
        else:
            super().__setitem__(key, value)

MICROSERVICES = empty_class()

MS_idx = 0
SOCK_idx = 1
UNSECURE_id = PASS_idx = 2
IV_idx = 3


from .clienthandler import ArchNetClientHandler
from .exception import *
from .response import *
from .microserviceclient import MicroserviceClient
