from ..default import MICROSERVICES, PASS_idx, IV_idx, MS_idx, SOCK_idx
from Crypto.PublicKey import RSA
from Crypto import Random
import yaml

def create_configuration_file(max_number = 500, max_req_size = 25000, port = 5000, hostname = 'localhost', config_file="server_config.yaml"):
    confs= {
        "max_number" : max_number,
        "max_req_size" : max_req_size,
        "port" : int(port),
        "hostname" : hostname,
        "MICROSERVICES" : {}
    }

    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator)

    confs["RSA_PUBLIC_KEY"] = key.publickey().exportKey()
    confs["RSA_PRIVATE_KEY"] = key.exportKey()

    with open(config_file, "w") as fp:
        yaml.safe_dump(confs, fp)

def add_microservice(config_file, name, port, hostname, passphrase=None, iv=None, socket_type = "keep_alive"):
    ms_dict = {}
    if passphrase is "random":
        passphrase = Random.new().read(32)
        iv = Random.new().read(16)

    if passphrase is not None:
        passphrase = b64encode(passphrase)
        iv = b64encode(iv)

    with open(config_file) as fp:
        configurations = yaml.safe_load(fp)

    ms_dict = {
        "port" : int(port),
        "hostname" : hostname,
        "passphrase" : passphrase,
        "iv" : iv,
        "socket" : socket_type
    }

    configurations["MICROSERVICES"][name] = ms_dict

    fpath = config_file[:config_file.rindex("/")+1]

    with open(config_file, "w") as fp:
        yaml.safe_dump(configurations, fp)

    with open(fpath + name + "_config.yaml", "w") as fp:
        yaml.safe_dump(ms_dict, fp)

def StartMicroservicesFromDict(dic):
    import copy
    def _clean_microservices():
        for ms_name in MICROSERVICES:
            if MICROSERVICES[ms_name]["passphrase"] is not None:
                MICROSERVICES[ms_name]["passphrase"] = b64decode(MICROSERVICES[ms_name]["passphrase"])
                MICROSERVICES[ms_name]["iv"] = b64decode(MICROSERVICES[ms_name]["iv"])
    for ms_name in dic:
        MICROSERVICES[ms_name] = copy.deepcopy(dic[ms_name])

def StartMicroservices(configuration_file):
    import yaml
    import copy
    def _clean_microservices():
        for ms_name in MICROSERVICES:
            if MICROSERVICES[ms_name]["passphrase"] is not None:
                MICROSERVICES[ms_name]["passphrase"] = b64decode(MICROSERVICES[ms_name]["passphrase"])
                MICROSERVICES[ms_name]["iv"] = b64decode(MICROSERVICES[ms_name]["iv"])

    with open(configuration_file) as fp:
        configuration = yaml.safe_load(fp)
    aux = configuration.get("MICROSERVICES",{})
    for ms_name in aux:
        MICROSERVICES[ms_name] = copy.deepcopy(aux[ms_name])

from .server import ArchNetServer
