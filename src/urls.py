from core.api import Api
from .viewsets.index import Index
from .viewsets.product import (
    CategoryViewsets,
    UnitViewsets,
    UnitDetail
)


def init(app) -> None:
    route = Api(app, prefix='')
    route.add_resource(Index, '/')
    api = Api(app, prefix='/v1')
    api.add_resource(UnitViewsets, "/products")
    api.add_resource(UnitDetail, "/products/<int:product_id>")
    api.add_resource(CategoryViewsets, "/categories")