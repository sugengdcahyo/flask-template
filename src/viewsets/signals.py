from flask import request
from flask_restful import Resource
from flask_restful import reqparse
from flask_jwt_extended import jwt_required
from core.worker import celery
from core.pusher import pusher_client

from threading import Thread
from concurrent.futures import ThreadPoolExecutor

import time

class SignalViewsets(Resource):

    def post(self, *args, **kwargs):
        param = request.get_json()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.submit(self.ota_traveloka)
            executor.submit(self.ota_booking)
            executor.submit(self.ota_tiket)

        return {
            "massage": "crawling finished." 
        }

    def ota_traveloka(self):
        # traveloka process
        time.sleep(10)
        pusher_client.trigger(
            'notify', 
            'refresh-rate', 
            {'message': 'crawling ota traveloka has been successfully.'}
        )

    def ota_booking(self):
        # booking process
        time.sleep(4)
        pusher_client.trigger(
            'notify', 
            'refresh-rate', 
            {'message': 'crawling ota booking has been successfully.'}
        )

    def ota_tiket(self):
        # tiket process
        time.sleep(4)
        pusher_client.trigger(
            'notify', 
            'refresh-rate', 
            {'message': 'crawling ota tiket has been successfully.'}
        )

    
    # to soon.
    @celery.task(name="refresh_rate_task")
    def test(self, data):
        self.ota_booking()
        self.ota_traveloka()
        self.ota_tiket()