from flask_restful import Resource
from core.elasticsearch import es

class Index(Resource):

    def get(self, *args, **kwargs):

        return {
            "message": "Hello human."
        }