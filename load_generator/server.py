from flask import Blueprint, jsonify, request
from .load_generator import LoadGenerator
from .config import *

lg = LoadGenerator()
load_generator = Blueprint('load_generator', __name__)

@load_generator.route("/configuration", methods=['GET'])
def getConfiguration():
    return jsonify(lg.getConfiguration())

@load_generator.route("/rrh/create", methods=['POST'])
def addRRH():
    return jsonify(lg.addRRH(float(request.args.get('rate'))))

@load_generator.route("/rrh/<id>/remove", methods=['POST'])
def removeRRH(id):
    lg.removeRRH(int(id))
    return jsonify({ 'success': True })

@load_generator.route("/rrh/<id>/set-arrival-rate", methods=['POST'])
def setArrivalRate(id):
    return jsonify(lg.setArrivalRate(int(id), float(request.args.get('rate'))))

@load_generator.route("/rrh/<id>/add-connection", methods=['POST'])
def addConnection(id):
    return jsonify(lg.addConnection(int(id), int(request.args.get('amount'))))

@load_generator.route("/rrh/<id>/remove-connection", methods=['POST'])
def removeConnection(id):
    return jsonify(lg.removeConnection(int(id), int(request.args.get('amount'))))

class LGServer():
    def __init__(self, app):
        app.register_blueprint(load_generator, url_prefix='/load-generator')
