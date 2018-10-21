from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
from .resource_mapper import ResourceMapper
from .config import *

resource_mapper = Blueprint('resource_mapper', __name__)

class RMServer():
    ref = None

    def __init__(self):
        RMServer.ref = ResourceMapper()
        app = Flask('resource-mapper')
        CORS(app)
        app.register_blueprint(resource_mapper, url_prefix='/resource-mapper')
        app.run(host='0.0.0.0', port=RM_SERVICE_PORT)

    @resource_mapper.route("/mapping/all", methods=['GET'])
    def getMapping():
        return jsonify(RMServer.ref.getCurrentMapping())

    @resource_mapper.route("/mapping", methods=['POST'])
    def addMapping():
        rrh = int(request.args.get('rrh'))
        if (request.args.get('format') is None or request.args.get('format') == 'id'):
            bbus = [int(id) for id in request.args.get('bbus').split(',')]
        else:
            bbus = [RMServer.ref.getHostIdByIP(ip) for ip in request.args.get('bbus').split(',')]
        return jsonify(RMServer.ref.addMapping(rrh, bbus).objectify())

    @resource_mapper.route("/mapping/<id>/remove", methods=['POST'])
    def removeMapping(id):
        RMServer.ref.removeMapping(int(id))
        return jsonify({ 'success': True })

    @resource_mapper.route("/mapping/<id>/update", methods=['POST'])
    def updateMapping(id):
        return jsonify(RMServer.ref.updateMapping(id, [int(id) for id in request.args.get('bbus').split(',')]))

    @resource_mapper.route("/topology", methods=['GET'])
    def getTopology():
        return jsonify(RMServer.ref.getTopology().objectify())

    @resource_mapper.route("/topology/update", methods=['POST'])
    def updateTopology():
        return jsonify(RMServer.ref.updateTopology().objectify())

    @resource_mapper.route("/topology/bbu-migration", methods=['POST'])
    def onBBUMigration():
        RMServer.ref.onBBUMigration(request.args.get('address'))
        return jsonify({ 'success': True })

    @resource_mapper.route("/topology/bbu-creation", methods=['POST'])
    def onBBUCreation():
        RMServer.ref.onBBUCreation(request.args.get('address'))
        return jsonify({ 'success': True })

    @resource_mapper.route("/topology/set-controller", methods=['POST'])
    def setControllerNodeSwitch():
        RMServer.ref.setControllerNodeSwitch(request.args.get('id'))
        return jsonify({ 'success': True })
