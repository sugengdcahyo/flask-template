from flask import Flask
from src.seeder.product import generate_product

def init_cli(app: Flask) -> Flask:
    app.cli.add_command(generate_product)
