from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
from .config import *
from .cloud_orchestrator.orchestrator import Orchestrator

openstack_client = Blueprint('openstack_client', __name__)

class OCServer():
    ref = None

    def __init__(self):
        OCServer.ref = Orchestrator()
        app = flask('openstack-client')
        CORS(app)
        app.register_blueprint(openstack_client, url_prefix='/openstack-client')
        app.run(host='0.0.0.0', port=SERVICE_PORT)
