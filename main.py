import time
# from resource_mapper import RMServer
from load_generator import LGServer

if __name__ == "__main__":
    lgServer = LGServer()
    # rmServer = RMServer()
    lgServer.run()
    # rmServer.run()
