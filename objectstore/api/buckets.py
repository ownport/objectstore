#
#   Operations on Buckets
#
#   Links:
#   - http://docs.aws.amazon.com/AmazonS3/latest/API/ErrorResponses.html
#

import os
import re
import json
import shutil
import falcon

from common import BaseAPI
from sqlitedict import SqliteDict


class BucketCollectionAPI(BaseAPI):

    def on_put(self, req, resp):
        ''' _PUT_ Bucket
        
        creates a new bucket.

        parameters:
        - name, mandatory parameter

        The rest of parameters are optional and they will storing as metadata

        Based on: [PUT Bucket](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTBucketPUT.html)
        '''
        if u'name' not in req.params:
            raise falcon.HTTPMissingParam('name')

        bucket_name = req.params.get(u'name')

        bucket = Bucket(bucket_name, storage_path=self._storage_path)
        bucket.metadata = req.params
        bucket.create()

        resp.data = json.dumps(bucket.info())


class BucketAPI(BaseAPI):

    def on_get(self, req, resp, bucket_name):
        ''' _GET_ Bucket (List Objects)
        
        returns some or all (up to 1000) of the objects in a bucket. You can use the request parameters 
        as selection criteria to return a subset of the objects in a bucket. 
        
        Based on: [GET Bucket (List Objects)](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTBucketGET.html)
        '''
        bucket = Bucket(bucket_name=bucket_name, storage_path=self._storage_path)
        if bucket.exists():
            resp.data = json.dumps({
                u'metadata': bucket.metadata,
                u'objects': bucket.object_list()
            })
        else:
            raise falcon.HTTPNotFound()


    def on_head(self, req, resp, bucket_name):
        ''' _HEAD_ Bucket
        
        useful to determine if a bucket exists.
        
        Based on: [HEAD Bucket](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTBucketHEAD.html)
        '''
        bucket = Bucket(bucket_name, storage_path=self._storage_path)
        if not bucket.exists():
            raise falcon.HTTPNotFound()


    def on_delete(self, req, resp, bucket_name):
        ''' _DELETE_ Bucket

        deletes the bucket named in the URI. All objects (including all object versions and delete markers) 
        in the bucket must be deleted before the bucket itself can be deleted.
        
        Based on: [DELETE Bucket](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTBucketDELETE.html)
        '''
        bucket = Bucket(bucket_name, storage_path=self._storage_path)
        if bucket and bucket.exists():
            bucket.delete()
        else:
            raise falcon.HTTPNotFound()


class Bucket(object):

    def __init__(self, bucket_name, storage_path=None):
        ''' Bucker init

        - if the bucket exists, meta parameter will be ignored

        '''
        if bucket_name and isinstance(bucket_name, (str, unicode)) and re.match(r"^[a-z0-9\.\-_]+$", bucket_name, re.I):
            self._name = bucket_name.strip()
        else:
            raise falcon.HTTPInvalidParam(
                "The parameter shall contain only alpha-numeric characters, value: '%s'" % bucket_name, 
                param_name='name'
            )

        self._bucket_path = None
        if storage_path and os.path.exists(storage_path):
            self._bucket_path = os.path.join(storage_path, self._name)
        else:
            raise falcon.HTTPInternalServerError(
                title='IncorrectStoragePath',
                description='The storage path is incorrect, "%s"' % storage_path
            )

        if self._bucket_path and os.path.exists(self._bucket_path):
            self._meta = SqliteDict(os.path.join(self._bucket_path,'metadata.sqlite'), 'bucket', autocommit=True)
        else:
            self._meta = SqliteDict(':memory:', 'bucket', autocommit=True)

    @property
    def bucket_path(self):

        return self._bucket_path

    
    @property
    def metadata(self):
        
        return dict(self._meta)
    

    @metadata.setter
    def metadata(self, value):

        if value and isinstance(value, dict):
            self._meta.update(value)
        else:
            raise RuntimeError('Incorrect metadata type. Found "%s", expected "dict"' % type(value))


    def exists(self):
        ''' check if the bucket exists
        ''' 
        if self.bucket_path and os.path.exists(self.bucket_path):       
            return True
        else:
            return False


    def create(self):
        ''' create new bucket
        '''
        if self.exists():
            raise falcon.HTTPConflict(
                title='BucketAlreadyExists',
                description="The requested bucket name '%s' is not available. Please select a different name and try again." % self._name
            )

        # prepare bucket directory
        try:
            os.makedirs(self.bucket_path)
            os.makedirs(os.path.join(self.bucket_path, 'data'))
            os.makedirs(os.path.join(self.bucket_path, 'tmp'))
        except IOError, err:
            raise falcon.HTTPInternalServerError(
                title='BucketCreationError',
                description='The path to bucket cannot be created, "%s"' % self.bucket_path
            )

        # create metadata file in bucket directory
        _meta = self._meta
        self._meta = SqliteDict(os.path.join(self.bucket_path, 'metadata.sqlite'), 'bucket', autocommit=True) 
        self._meta.update(_meta)


    def delete(self):
        ''' delete bucket. 

        Note: The bucket will be removed only if all objects are removed into bucket
        '''
        bucket_data_path = os.path.join(self.bucket_path, 'data')
        if self.bucket_path and os.path.isdir(self.bucket_path):
            if len(os.listdir(bucket_data_path)) > 0:
                raise falcon.HTTPConflict(
                    title='BucketNotEmpty',
                    description="The bucket you tried to delete is not empty"                    
                )
            else:
                shutil.rmtree(self.bucket_path)
        else:
            raise falcon.HTTPNotFound()


    def info(self):
        ''' returns bucket info as dictionary
        '''
        return dict(self._meta)


    def object_list(self):
        ''' returns a list of objects
        '''
        objects_metadata = SqliteDict(self._meta.filename, 'objects')
        return objects_metadata.keys()



class BucketCollection(object):

    def __init__(self, storage_path=None):

        self._storage_path = None
        if storage_path and os.path.exists(storage_path):
            self._storage_path = storage_path
        else:
            raise falcon.HTTPInternalServerError(
                title='IncorrectStoragePath',
                description='The storage path is incorrect, "%s"' % storage_path
            )

    def list(self):
        ''' return the list of buckets
        '''
        buckets_info = list()

        for bucket_name in os.listdir(self._storage_path):
            path = os.path.join(self._storage_path, bucket_name)
            if os.path.isdir(path):
                bucket = Bucket(bucket_name=bucket_name, storage_path=self._storage_path)
                buckets_info.append(bucket.info())

        return buckets_info
