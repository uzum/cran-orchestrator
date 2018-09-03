from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
from .config import *
from .log_collector import LogCollector

log_collector = Blueprint('log_collector', __name__)

class LCServer():
    ref = None

    def __init__(self):
        LCServer.ref = LogCollector()
        app = Flask('log-collector')
        CORS(app)
        app.register_blueprint(log_collector, url_prefix='/log-collector')
        app.run(host='0.0.0.0', port=LC_SERVICE_PORT)

    @log_collector.route("/peek", methods=['GET'])
    def peek():
        return jsonify(LCServer.ref.peek(int(request.args.get('index'))))

    @log_collector.route("/append", methods=['POST'])
    def append():
        return jsonify(LCServer.ref.append(request.json))
