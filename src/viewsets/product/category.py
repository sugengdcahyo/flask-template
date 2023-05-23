from flask_restful import (
    request, 
    Resource
)

from src.models import Category
from src.serializers.product import (
    CategorySerializer, 
    ProductSerializer
)
import os

class CategoryViewsets(Resource):
    serializer_class = CategorySerializer
    instance = Category

    def get(self, *args, **kwargs):
        # print(os.getcwd())
        image_dir = os.path.join(os.getcwd(), 'image/2.jpg')
        print(os.path.isfile(image_dir))
        instances = self.instance.query.all()

        serializer = CategorySerializer(many=True).dump(instances)
        print(serializer)
        return serializer
