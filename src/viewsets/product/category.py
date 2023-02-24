from flask_restful import (
    request, 
    Resource
)

from src.models import Category
from src.serializers.product import (
    CategorySerializer, 
    ProductSerializer
)

class CategoryViewsets(Resource):
    serializer_class = CategorySerializer
    instance = Category

    def get(self, *args, **kwargs):
        instances = self.instance.query.all()

        serializer = CategorySerializer(many=True).dump(instances)
        print(serializer)
        return serializer