from flask import Flask, jsonify, request
from .resource_mapper import ResourceMapper
from .config import *

app = Flask('resource_mapper')
rm = ResourceMapper()

@app.route("/mapping/all", methods=['GET'])
def getMapping():
    return jsonify(rm.getCurrentMapping())

@app.route("/mapping", methods=['POST'])
def addMapping():
    rrh = int(request.args.get('rrh'))
    bbus = [int(id) for id in request.args.get('bbus').split(',')]
    return jsonify(rm.addMapping(rrh, bbus).objectify())

@app.route("/mapping/<id>/remove", methods=['POST'])
def removeMapping(id):
    rm.removeMapping(id)
    return "OK"

@app.route("/topology/set-controller", methods=['POST'])
def setControllerNodeSwitch():
    rm.setControllerNodeSwitch(request.args.get('id'))
    return "OK"

class RMServer():
    def run(self):
        app.run(port=SERVICE_PORT)
