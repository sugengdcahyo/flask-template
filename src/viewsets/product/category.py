from flask_restful import (
    request, 
    Resource
)

from src.models import Category

class CategoryViewsets(Resource):

    def get(self, *args, **kwargs):
        return {"categories": []}