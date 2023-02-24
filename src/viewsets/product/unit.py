from flask_restful import (
    request, 
    Resource
)

from src.models import Product
from src.serializers.product import ProductSerializer

class UnitViewsets(Resource):
    serializer_class = ProductSerializer
    instance = Product

    def get(self, *args, **kwargs):
        instance = self.instance.query.all()
        
        response = []
        for data in instance:
            response.append({
                "_id": data._id,
                "name": data.name,
                "price": data.price
            })

        return response, 201
        
    
    def post(self,):
        return {}
    