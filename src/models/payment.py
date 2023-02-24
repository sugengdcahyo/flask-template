from .mixin import Base
from .product import Product

from core.database import db
from sqlalchemy.orm import relationship

class Invoice(Base):
    __tablename__ = "payment_invoice"
    products = relationship(
        "Product", backref="Invoice", secondary="payment_order"
    )


class Order(Base):
    __tablename__ = "payment_order"
    product_id = db.Column(db.Integer, db.ForeignKey(Product._id))
    invoice_id = db.Column(db.Integer, db.ForeignKey(Invoice._id))