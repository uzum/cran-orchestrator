from flask import Flask, jsonify, request
from .resource_mapper import ResourceMapper

app = Flask('odl_restconf')
rm = ResourceMapper()

@app.route("/mapping/all", methods=['GET'])
def getMapping():
    return jsonify(rm.getCurrentMapping())

@app.route("/mapping", methods=['POST'])
def addMapping():
    rrh = request.args.get('rrh')
    bbus = request.args.get('bbus')
    return "mapping: from " + rrh + " to " + bbus

@app.route("/mapping/<id>/remove", methods=['POST'])
def removeMapping(id):
    rm.removeMapping(id)
    return "OK"

class Server():
    def run(self):
        app.run()
