from flask import Blueprint, jsonify, request
from .resource_mapper import ResourceMapper
from .config import *

rm = ResourceMapper()
resource_mapper = Blueprint('resource_mapper', __name__)

@resource_mapper.route("/mapping/all", methods=['GET'])
def getMapping():
    return jsonify(rm.getCurrentMapping())

@resource_mapper.route("/mapping", methods=['POST'])
def addMapping():
    rrh = int(request.args.get('rrh'))
    bbus = [int(id) for id in request.args.get('bbus').split(',')]
    return jsonify(rm.addMapping(rrh, bbus).objectify())

@resource_mapper.route("/mapping/<id>/remove", methods=['POST'])
def removeMapping(id):
    rm.removeMapping(id)
    return jsonify({ 'success': True }) 

@resource_mapper.route("/topology/set-controller", methods=['POST'])
def setControllerNodeSwitch():
    rm.setControllerNodeSwitch(request.args.get('id'))
    return jsonify({ 'success': True }) 

class RMServer():
    def __init__(self, app):
        app.register_blueprint(resource_mapper, url_prefix='/resource-mapper')
