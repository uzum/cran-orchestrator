from flask import Flask, jsonify, request
from .load_generator import LoadGenerator
from .config import *

app = Flask('load_generator')
lg = LoadGenerator()

@app.route("/configuration", methods=['GET'])
def getConfiguration():
    return jsonify(lg.getConfiguration())

class LGServer():
    def run(self):
        app.run(port=SERVICE_PORT)
