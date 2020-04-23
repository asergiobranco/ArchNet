#!/usr/bin/python

import sys, getopt
import webbrowser
import pkgutil
import http.server
import socketserver
import os
from multiprocessing import Process
from random import randint


from .server import ArchNetServer, create_configuration_file, add_microservice

def read_the_docs(**kwargs):
    """Opens a small web app where the documentation is available.
    """
    this_dir, this_filename = os.path.split(__file__)
    DATA_PATH = os.path.join(this_dir, "html_docs/")
    os.chdir(DATA_PATH)
    PORT = 10000 + randint(0, 307)
    HOSTNAME = "localhost"
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer((HOSTNAME, PORT), Handler) as httpd:
        print("Please, go to: http://%s" % (HOSTNAME + ":" + str(PORT)))
        p = Process(target=httpd.serve_forever)
        p.start()
        webbrowser.open(HOSTNAME + ":" + str(PORT))
        p.join()

def _start_server(**kwargs):
    server = ArchNetServer(**kwargs)
    print("Server Starting...")
    server.start()

def _switch(case):
    return {
        "config"              : lambda option_dict : create_configuration_file(**option_dict),
        "start"               : lambda option_dict : _start_server(**option_dict),
        "add-microservice"    : lambda option_dict : add_microservice(**option_dict),
        "documentation"       : lambda option_dict : read_the_docs(**option_dict)
    }.get(case)

def _parse_args(argv):
    try:
        opts, args = getopt.getopt(argv, "", ["config", "start", "add-microservice", "documentation", "config_file=", "port=", "hostname=", "passphrase=", "iv=", "socket_type=", "name="])
    except getopt.GetoptError as e:
        print("Unrecognized option: %s" % (e.opt))
        sys.exit(2)

    option_dict = {}
    cases = []
    for opt, arg in opts:
        if len(arg):
            option_dict[opt[2:]] = arg
        else:
            cases.append(opt[2:])
    if len(cases) == 1:
        _switch(cases[0])(option_dict)
    else:
        print("Only an option can be passed")

if __name__ == "__main__":
    _parse_args(sys.argv[1:])
