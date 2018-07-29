from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
from .load_generator import LoadGenerator
from .config import *

load_generator = Blueprint('load_generator', __name__)

class LGServer():
    ref = None

    def __init__(self):
        LGServer.ref = LoadGenerator()
        app = Flask('load-generator')
        CORS(app)
        app.register_blueprint(load_generator, url_prefix='/load-generator')
        app.run(host='0.0.0.0', port=LG_SERVICE_PORT)

    @load_generator.route("/configuration", methods=['GET'])
    def getConfiguration():
        return jsonify(LGServer.ref.getConfiguration())

    @load_generator.route("/rrh/create", methods=['POST'])
    def addRRH():
        return jsonify(LGServer.ref.addRRH(float(request.args.get('rate'))))

    @load_generator.route("/rrh/<id>/remove", methods=['POST'])
    def removeRRH(id):
        LGServer.ref.removeRRH(int(id))
        return jsonify({ 'success': True })

    @load_generator.route("/rrh/<id>/set-arrival-rate", methods=['POST'])
    def setArrivalRate(id):
        return jsonify(LGServer.ref.setArrivalRate(int(id), float(request.args.get('rate'))))

    @load_generator.route("/rrh/<id>/add-connection", methods=['POST'])
    def addConnection(id):
        return jsonify(LGServer.ref.addConnection(int(id), int(request.args.get('amount'))))

    @load_generator.route("/rrh/<id>/remove-connection", methods=['POST'])
    def removeConnection(id):
        return jsonify(LGServer.ref.removeConnection(int(id), int(request.args.get('amount'))))
