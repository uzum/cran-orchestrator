from flask import Flask, jsonify, request
from .load_generator import LoadGenerator

app = Flask('odl_restconf')
lg = LoadGenerator()

class Server():
    def run(self):
        app.run()
