from flask_restful import Api
from collections import OrderedDict

class Api(Api):

    def make_response(self, data, *args, **kwargs):
        status_code = args[0]
        keys = ["data", "paginate", "status", "status_code"]
        paginate = None

        try:
            if data.get("paginate") and data.get("results"):
                paginate = data["paginate"]
                data.pop("paginate")
                data = data.get("results", [])
        except:
            pass
        
        status = "success" if ( status_code >= 200 and status_code < 400 ) else "failed"
        data = {
            "data": data,
            "status": status,
            "status_code": status_code
        }
        if paginate: data['paginate'] = paginate
        
        return super().make_response(data, *args, **kwargs)