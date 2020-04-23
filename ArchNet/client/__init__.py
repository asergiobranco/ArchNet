from .client import ArchNetClient
from .socket import ArchNetSocketClient

def read_the_docs():
    import pkgutil
    data = pkgutil.get_data(__package__, 'readme.md')
    print(data.decode("utf-8"))
