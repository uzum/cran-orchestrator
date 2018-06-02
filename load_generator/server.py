from flask import Blueprint, jsonify, request
from .load_generator import LoadGenerator
from .config import *

lg = LoadGenerator()
load_generator = Blueprint('load_generator', __name__)

@load_generator.route("/configuration", methods=['GET'])
def getConfiguration():
    response = jsonify(lg.getConfiguration())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@load_generator.route("/rrh/create", methods=['POST'])
def addRRH():
    response = jsonify(lg.addRRH(float(request.args.get('rate'))))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@load_generator.route("/rrh/<id>/remove", methods=['POST'])
def removeRRH(id):
    lg.removeRRH(int(id))
    response = jsonify({ 'success': True })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@load_generator.route("/rrh/<id>/set-arrival-rate", methods=['POST'])
def setArrivalRate(id):
    response = jsonify(lg.setArrivalRate(int(id), float(request.args.get('rate'))))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@load_generator.route("/rrh/<id>/add-connection", methods=['POST'])
def addConnection(id):
    response = jsonify(lg.addConnection(int(id), int(request.args.get('amount'))))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@load_generator.route("/rrh/<id>/remove-connection", methods=['POST'])
def removeConnection(id):
    response = jsonify(lg.removeConnection(int(id), int(request.args.get('amount'))))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

class LGServer():
    def __init__(self, app):
        app.register_blueprint(load_generator, url_prefix='/load-generator')
