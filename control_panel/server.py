from flask import Flask
from .config import *

class CPServer():
    def __init__(self):
        app = Flask('control-panel', static_url_path='', static_folder='control_panel')
        app.run(host='0.0.0.0', port=SERVICE_PORT)
