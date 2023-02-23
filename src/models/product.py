from .mixin import Base
from core.database import db 

from sqlalchemy.orm import (relationship)


class Category(Base):
    __tablename__ = "product_category"
    name = db.Column(db.String(125), nullable=False, unique=True)


class Product(Base):
    __tablename__ = "product_unit"
    name = db.Column(db.String(125), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    categories = relationship(
        "Category", 
        secondary="product_unit_categories", 
        backref="Product"
    )


class UnitCategories(Base):
    __tablename__ = "product_unit_categories"
    unit_id = db.Column(db.Integer, db.ForeignKey(Product._id))
    category_id = db.Column(db.Integer, db.ForeignKey(Category._id))