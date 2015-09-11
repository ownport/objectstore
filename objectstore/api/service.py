# 
#   Operations on the Service:
#

import os
import json

from common import BaseAPI
from buckets import BucketCollection

class ServiceAPI(BaseAPI):
    ''' returns a list of all buckets
    '''
    def on_get(self, req, resp):
        ''' returns a list of all buckets

        Based on: [GET Service](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTServiceGET.html)
        '''
        buckets = BucketCollection(self._storage_path)

        resp.data = json.dumps({
            'buckets': buckets.list()
        })



        