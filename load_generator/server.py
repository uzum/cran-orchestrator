from flask import Flask, jsonify, request
from .load_generator import LoadGenerator
from .config import *

app = Flask('load_generator')

lg = LoadGenerator()

@app.route("/configuration", methods=['GET'])
def getConfiguration():
    response = jsonify(lg.getConfiguration())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/rrh/create", methods=['POST'])
def addRRH():
    response = jsonify(lg.addRRH(float(request.args.get('rate'))))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/rrh/<id>/remove", methods=['POST'])
def removeRRH(id):
    lg.removeRRH(int(id))
    response = jsonify({ 'success': True })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/rrh/<id>/set-arrival-rate", methods=['POST'])
def setArrivalRate(id):
    response = jsonify(lg.setArrivalRate(int(id), float(request.args.get('rate'))))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/rrh/<id>/add-connection", methods=['POST'])
def addConnection(id):
    response = jsonify(lg.addConnection(int(id), int(request.args.get('amount'))))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/rrh/<id>/remove-connection", methods=['POST'])
def removeConnection(id):
    response = jsonify(lg.removeConnection(int(id), int(request.args.get('amount'))))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

class LGServer():
    def run(self):
        app.run(port=SERVICE_PORT)
