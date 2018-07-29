from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
from .config import *

log_collector = Blueprint('log_collector', __name__)

class LCServer():
    def __init__(self):
        app = Flask('log-collector')
        CORS(app)
        app.register_blueprint(log_collector, url_prefix='/log-collector')
        app.run(host='0.0.0.0', port=LC_SERVICE_PORT)
