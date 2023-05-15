from src.models.product import Product
from flask.cli import AppGroup

import click

cli_app = AppGroup()

PRODUCTS = [
    {
        "name": "sabun",
        "price": 1000
    },
    {
        "name": "sikat gigi",
        "price": 500
    }
]

@cli_app.command("generate")
# @click.option()
def generate_product():
    for product in PRODUCTS:
        try:
            data = Product(
                **product
            )
            data.save()
        except BaseException as e:
            print(str(e))

    print("finish")