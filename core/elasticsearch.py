from elasticsearch import Elasticsearch
from flask_elasticsearch import FlaskElasticsearch

es = FlaskElasticsearch()

def init_app(app):
    app.config['ELASTICSEARCH_HOST'] = 'https://es.horison.datains.id:80'
    app.config['ELASTICSEARCH_USE_SSL'] = False
    app.config['ELASTICSEARCH_USERNAME'] = 'datains'
    app.config['ELASTICSEARCH_PASSWORD'] = 'Data1n5'
    es.init_app(app)