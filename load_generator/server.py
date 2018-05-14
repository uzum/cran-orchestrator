from flask import Flask, jsonify, request
from .load_generator import LoadGenerator
from .config import *

app = Flask('load_generator')
lg = LoadGenerator()

@app.route("/configuration", methods=['GET'])
def getConfiguration():
    return jsonify(lg.getConfiguration())

@app.route("/rrh/create", methods=['POST'])
def addRRH():
    return jsonify(lg.addRRH(float(request.args.get('rate'))))

@app.route("/rrh/<id>/remove", methods=['POST'])
def removeRRH(id):
    lg.removeRRH(int(id))
    return "OK"

@app.route("/rrh/<id>/set-arrival-rate", methods=['POST'])
def setArrivalRate(id):
    return jsonify(lg.setArrivalRate(int(id), float(request.args.get('rate'))))

@app.route("/rrh/<id>/add-connection", methods=['POST'])
def addConnection(id):
    return jsonify(lg.addConnection(int(id), int(request.args.get('amount'))))

@app.route("/rrh/<id>/remove-connection", methods=['POST'])
def removeConnection(id):
    return jsonify(lg.removeConnection(int(id), int(request.args.get('amount'))))

class LGServer():
    def run(self):
        app.run(port=SERVICE_PORT)
