from flask import Blueprint, jsonify, request
from .resource_mapper import ResourceMapper
from .config import *

rm = ResourceMapper()
resource_mapper = Blueprint('resource_mapper', __name__)

@resource_mapper.route("/mapping/all", methods=['GET'])
def getMapping():
    # return "[]"
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

@resource_mapper.route("/topology", methods=['GET'])
def getTopology():
    # return jsonify({
    #     'controllerNode': {
    #         'id': 'switch#0',
    #         'hosts': []
    #     },
    #     'computeNodes': [{
    #         'id': 'switch#1',
    #         'hosts': [
    #             { 'id': 'host1', 'mac':'AA:11', 'ip': '10.1' },
    #             { 'id': 'host2', 'mac':'AA:12', 'ip': '10.2' },
    #             { 'id': 'host3', 'mac':'AA:13', 'ip': '10.3' }
    #         ]
    #     }, {
    #         'id': 'switch#2',
    #         'hosts': [
    #             { 'id': 'host4', 'mac':'AA:21', 'ip': '20.1' },
    #             { 'id': 'host5', 'mac':'AA:22', 'ip': '20.2' },
    #             { 'id': 'host6', 'mac':'AA:23', 'ip': '20.3' }
    #         ]
    #     }, {
    #         'id': 'switch#3',
    #         'hosts': [
    #             { 'id': 'host7', 'mac':'AA:31', 'ip': '30.1' },
    #             { 'id': 'host8', 'mac':'AA:32', 'ip': '30.2' },
    #             { 'id': 'host9', 'mac':'AA:33', 'ip': '30.3' }
    #         ]
    #     }]
    # })
    return jsonify(rm.getTopology().objectify())

@resource_mapper.route("/topology/set-controller", methods=['POST'])
def setControllerNodeSwitch():
    rm.setControllerNodeSwitch(request.args.get('id'))
    return jsonify({ 'success': True })

class RMServer():
    def __init__(self, app):
        app.register_blueprint(resource_mapper, url_prefix='/resource-mapper')
