import requests
from flask import Flask, Blueprint, Response, stream_with_context, request

from .config import *

control_panel = Blueprint('control-panel', __name__)

class CPServer():
    def __init__(self):
        app = Flask('control-panel', static_url_path='', static_folder='control_panel')
        app.register_blueprint(control_panel, url_prefix='')
        app.run(host='0.0.0.0', port=CP_SERVICE_PORT)

    @control_panel.route("/openstack-client/<path:url>", methods=["GET", "POST"])
    def OCProxy(url):
        if (request.method == 'GET'):
            req = requests.get(OC_SERVICE_URL + '/openstack-client/' + url, stream=True, params=request.args)
        else:
            req = requests.post(OC_SERVICE_URL + '/openstack-client/' + url, stream=True, params=request.args)
        return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])

    @control_panel.route("/resource-mapper/<path:url>", methods=["GET", "POST"])
    def RMProxy(url):
        if (request.method == 'GET'):
            req = requests.get(RM_SERVICE_URL + '/resource-mapper/' + url, stream=True, params=request.args)
        else:
            req = requests.post(RM_SERVICE_URL + '/resource-mapper/' + url, stream=True, params=request.args)
        return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])

    @control_panel.route("/load-generator/<path:url>", methods=["GET", "POST"])
    def LGProxy(url):
        if (request.method == 'GET'):
            req = requests.get(LG_SERVICE_URL + '/load-generator/' + url, stream=True, params=request.args)
        else:
            req = requests.post(LG_SERVICE_URL + '/load-generator/' + url, stream=True, params=request.args)
        return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])

    @control_panel.route("/log-collector/<path:url>", methods=["GET", "POST"])
    def LCProxy(url):
        if (request.method == 'GET'):
            req = requests.get(LC_SERVICE_URL + '/log-collector/' + url, stream=True, params=request.args)
        else:
            req = requests.post(LC_SERVICE_URL + '/log-collector/' + url, stream=True, params=request.args)
        return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])
