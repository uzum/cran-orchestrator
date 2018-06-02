import time
from flask import Flask
# from resource_mapper import RMServer
from load_generator import LGServer

app = Flask('cran-orchestrator', static_url_path='', static_folder='control_panel')

if __name__ == "__main__":
    lgServer = LGServer(app)
    app.run(host='0.0.0.0', port=5000)
    # rmServer = RMServer()
