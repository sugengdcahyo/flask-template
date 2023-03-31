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

        return response, 200

    def post(self,):
        instance = Product(**request.get_json())
        try:
            instance.save()
        except BaseException as e:
            return {"error": e.orig}, 400

        return {
            "_id": instance._id,
            "name": instance.name,
            "price": instance.price
        }


class UnitDetail(Resource):
    instance = Product

    def put(self, product_id, *args, **kwargs):
        params = request.get_json()
        instance = self.instance.query.filter_by(_id=product_id).one_or_none()
        
        if instance:
            instance.name = params.get("name", None)
            instance.price = params.get("price", None)
            try:
                instance.save()
            except BaseException as e:
                return {"error": str(e.orig)}, 400

        else:
            return {"error": "Data not found"}, 404

        return {
            "_id": instance._id,
            "name": instance.name,
            "price": instance.price
        }

    def delete(self, product_id, *args, **kwargs):
        instance = self.instance.query.filter_by(_id=product_id).one_or_none()
        if instance:
            instance.delete()
        else:
            return {"error": "Data not found."}, 404

        return {"message": "Data deleted."}, 200
