from datetime import datetime, date

import isodate as iso
from bson import ObjectId
from flask.json import JSONEncoder
from werkzeug.routing import BaseConverter


class MongoJSONEncoder(JSONEncoder):
    def default(self, o):
        print(o)
        if isinstance(o, (datetime, date)):
            return iso.datetime_isoformat(o)
        if isinstance(o, ObjectId):
            #o['id'] = str(o['_id'])
            return str(o)
        else:
            return super().default(o)

    #def get(self):

class ObjectIdConverter(BaseConverter):
    def to_python(self, value):
        return ObjectId(value)

    def to_url(self, value):
        return str(value)