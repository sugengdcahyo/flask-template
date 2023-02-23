from core.api import Api
from .viewsets.index import Index
from .viewsets.signals import SignalViewsets

def init(app) -> None:
    route = Api(app, prefix='')
    route.add_resource(Index, '/')
    api = Api(app, prefix='/v1')
    api.add_resource(SignalViewsets, '/services/stream')