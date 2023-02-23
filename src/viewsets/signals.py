from flask import request
from flask_restful import Resource


class SignalViewsets(Resource):

    def post(self, *args, **kwargs):
        return {}