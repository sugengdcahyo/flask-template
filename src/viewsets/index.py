from flask_restful import Resource


class Index(Resource):

    def get(self, *args, **kwargs):

        return {
            "message": "Hello human."
        }