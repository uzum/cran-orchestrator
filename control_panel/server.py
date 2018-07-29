import requests
from flask import Flask, Blueprint, Response, stream_with_context

from .config import *

control_panel = Blueprint('control-panel', __name__)

class CPServer():
    def __init__(self):
        app = Flask('control-panel', static_url_path='', static_folder='control_panel')
        app.register_blueprint(control_panel, url_prefix='')
        app.run(host='0.0.0.0', port=CP_SERVICE_PORT)

    @control_panel.route("/openstack-client/<url>")
    def OCProxy(url):
        req = requests.get(OC_SERVICE_URL + '/openstack-client/' + url, stream = True)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])

    @control_panel.route("/resource-mapper/<url>")
    def RMProxy(url):
        req = requests.get(RM_SERVICE_URL + '/resource-mapper/' + url, stream = True)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])

    @control_panel.route("/load-generator/<url>")
    def LGProxy(url):
        print("here")
        req = requests.get(LG_SERVICE_URL + '/load-generator/' + url, stream = True)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])

    @control_panel.route("/log-collector/<url>")
    def LCProxy(url):
        req = requests.get(LC_SERVICE_URL + '/log-collector/' + url, stream = True)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
