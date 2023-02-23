from flask_restful import (
    request, 
    Resource
)

from src.models import Product

class UnitViewsets(Resource):

    def get(self, *args, **kwargs):
        return {"products": []}