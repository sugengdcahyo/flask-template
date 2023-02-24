from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow.schema import Schema

from src.models.product import Product, Category, UnitCategories


class CategorySerializer(SQLAlchemySchema):
    _id = fields.Integer(load=True, partial=True)
    # name = fields.String()

    class Meta:
        model = Category
        fields = ["_id", "name"]


class ProductCategorySerializer(SQLAlchemySchema):
    category = fields.Method("get_category")

    class Meta:
        model = UnitCategories
        fields = ("category",)

    def get_category(self, instance):
        serializer = CategorySerializer(many=False).dump(instance)
        return serializer


class ProductSerializer(SQLAlchemySchema):
    _id = fields.Integer(load=True, partial=True)
    name = fields.String()
    categories = fields.Method("get_categories")

    class Meta:
        model = Product

    def get_categories(self, instance, *args, **kwargs):
        categories = UnitCategories.query.filter_by(unit_id=instance._id).all()
        product_category = ProductCategorySerializer(many=True).dump(categories)
        return product_category

    

