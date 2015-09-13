#
#   Operations on Objects
#
#   Links:
#   - http://docs.aws.amazon.com/AmazonS3/latest/API/ErrorResponses.html
#

import os
import json
import falcon
import shutil
import hashlib
import tempfile
import gunicorn

from common import BaseAPI
from buckets import Bucket

from sqlitedict import SqliteDict


def get_metadata_from_headers(headers):
    ''' returns metadata dict from Request headers

    [RFC 2616, Header Field Definitions](http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html)
    '''
    metadata = dict()
    content_length = int(headers.get('CONTENT-LENGTH', 0))
    if content_length:
        metadata['content-length'] = content_length

    content_md5 = headers.get('CONTENT-MD5', None)
    if content_md5:
        metadata['content-md5'] = content_md5

    content_sha1 = headers.get('CONTENT-SHA1', None)
    if content_sha1:
        metadata['content-sha1'] = content_sha1

    content_type = headers.get('CONTENT-TYPE', None)
    if content_type:
        metadata['content-type'] = content_type

    return metadata


def pairtree_path(filehash, pairs=2):
    ''' returns pairtree path based on filehash value
    
    filehash value: string like fa0ec35541f4f17a68e3d03acd04146f39ae5d2e
    
    >>> pairtree_path('fa0ec35541f4f17a68e3d03acd04146f39ae5d2e', pairs=2)
    '/fa/0e/fa0ec35541f4f17a68e3d03acd04146f39ae5d2e
    '''
    path = ''
    if len(filehash) <= 2 * pairs:
        raise RuntimeError('The file hash is too short. Expected more then %d, detected %d' % (2 * pairs, len(filehash)))
    for i in range(pairs):
        path = os.path.join(path, filehash[2*i:2*i+2])
    return os.path.join(path, filehash)


def movefile(source, target):
    ''' move file from source to target. 
    If target directory doesn't exist, it will create it
    '''
    target_dir = os.path.dirname(target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    shutil.move(source, target)


class ObjectAPI(BaseAPI):

    def __init__(self, storage_path):
        ''' __init__
        '''
        super(ObjectAPI, self).__init__(storage_path)
        self._bucket_path = None


    def on_put(self, req, resp, bucket_name, object_id):
        ''' _PUT_ Object

        adds an object to a bucket. 

        To ensure that data is not corrupted traversing the network, use the Content-MD5 header.
        
        Based on: [PUT Object](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPUT.html)
        '''
        metadata = get_metadata_from_headers(req.headers)

        # in case of adding object to a bucket, the object-id attribute is used as a content name
        metadata['content-name'] = object_id

        bucket = Bucket(bucket_name=bucket_name, storage_path=self._storage_path)

        if bucket.exists():
            bucket_object = BucketObject(bucket=bucket)
            bucket_object.metadata = metadata
            if not bucket_object.exists():
                bucket_object.store(req.stream)
                resp.data = json.dumps(bucket_object.info())
        else:
            raise falcon.HTTPBadRequest(
                title='InvalidBucketName', 
                description='The specified bucket is not valid',
            )


    def on_post(self, req, resp, bucket_name):
        ''' _POST_ Object

        adds an object to a specified bucket using HTML forms. POST is an alternate form of PUT that 
        enables browser-based uploads as a way of putting objects in buckets. Parameters that are 
        passed to PUT via HTTP Headers are instead passed as form fields to POST in the multipart/form-data 
        encoded message body. The service never stores partial objects: if you receive a successful response, 
        you can be confident the entire object was stored.

        Based on: [POST Object](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html)
        '''
        raise NotImplementedError()        


    def on_head(self, req, resp, bucket_name, object_id):
        ''' _HEAD_ Object

        retrieves metadata from an object without returning the object itself. This operation is useful 
        if you are interested only in an object's metadata.

        Based on: [HEAD Object](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectHEAD.html)
        '''
        bucket_object = BucketObject(
            object_id=object_id,
            bucket=Bucket(bucket_name=bucket_name, storage_path=self._storage_path)
        )
        if bucket_object.exists():
            for k,v in bucket_object.metadata.items():
                resp.set_header(k,v)
        else:
            raise falcon.HTTPNotFound()



    def on_get(self, req, resp, bucket_name, object_id):
        ''' _GET_ Object

        retrieves objects from the service. An bucket has no directory hierarchy such as you would 
        find in a typical computer file system. You can, however, create a logical hierarchy by using object 
        key names that imply a folder structure. For example, instead of naming an object sample.jpg, you can 
        name it photos/2006/February/sample.jpg. 

        Based on: [GET Object](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectGET.html)
        '''
        bucket_object = BucketObject(
            object_id=object_id,
            bucket=Bucket(bucket_name=bucket_name, storage_path=self._storage_path)
        )
        if bucket_object.exists():
            if 'content-type' in bucket_object.metadata:
                resp.content_type = bucket_object.metadata['content-type']
            for k,v in bucket_object.metadata.items():
                resp.set_header(k,v)
            resp.stream = open(bucket_object.filepath, 'rb')
            resp.stream_len = bucket_object.metadata['content-length']

        else:
            raise falcon.HTTPNotFound()


    def on_delete(self, req, resp, bucket_name, object_id):
        ''' _DELETE_ Object

        removes the object

        Based on: [DELETE Object](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectDELETE.html)
        '''
        bucket_object = BucketObject(
            object_id=object_id,
            bucket=Bucket(bucket_name=bucket_name, storage_path=self._storage_path)
        )
        if bucket_object.exists():
            bucket_object.delete()
        else:
            raise falcon.HTTPNotFound()



class BucketObject(object):

    def __init__(self, object_id=None, metadata={}, bucket=None):

        self.object_id = object_id

        self._bucket = bucket
        if bucket and isinstance(bucket, Bucket) and bucket.exists():
            self._bucket = bucket
            self._temp_path = os.path.join(self._bucket.bucket_path, 'tmp')
            self._data_path = os.path.join(self._bucket.bucket_path, 'data')
        else:
            raise falcon.HTTPBadRequest(
                title='InvalidBucketName', 
                description= 'The specified bucket is not valid'
            )

        # metadata key used for object identification in the storage
        self._metadata = dict()
        if 'object-key' in self._bucket.metadata and self._bucket.metadata['object-key'] in ['content-md5', 'content-sha1']:            
            self.OBJECT_KEY_BASE=self._bucket.metadata['object-key']
        else:
            self.OBJECT_KEY_BASE='content-sha1'
        self._objects_metadata = SqliteDict(os.path.join(bucket.bucket_path,'metadata.sqlite'), 'objects', autocommit=True)


    @property
    def metadata(self):

        if self.object_id and self.object_id in self._objects_metadata:
            return dict(self._objects_metadata[self.object_id])
        else:
            return self._metadata
    

    @metadata.setter
    def metadata(self, value):

        if value and isinstance(value, dict):

            # object_id doesn't set but object_id is in the value 
            if not self.object_id and self.OBJECT_KEY_BASE in value:
                self.object_id = value[self.OBJECT_KEY_BASE]

            # object_id is assigned
            if self.object_id:
                self._objects_metadata[self.object_id] = value
            
            # no object_id, stored temporary
            else:
                self._metadata = value    

        else:
            raise RuntimeError('Incorrect metadata type. Found "%s", expected "dict"') % type(value)

    @property
    def filepath(self):
        ''' returns the path to file in storage
        '''
        if self.object_id:
            return os.path.join(self._data_path, pairtree_path(self.object_id))
        else:
            return os.path.join(self._data_path, pairtree_path(self._metadata[self.OBJECT_KEY_BASE]))


    def exists(self):
        ''' returns True if the object is in the storage
        '''
        if self.object_id and self.object_id in self._objects_metadata:
            return True
        else:
            return False


    def store(self, stream=None):
        ''' store object into bucket
        '''

        # TODO: for later analysis

        # if not stream or not isinstance(stream, gunicorn.http.body.Body):
        #     raise falcon.HTTPInternalServerError(
        #         title = 'InvalidStreamType',
        #         description = 'The Stream type is invalid, %s' % type(stream)
        #     )

        if not stream:
            raise falcon.HTTPInternalServerError(
                title = 'FileEmpty',
                description = 'Attempt to store empty file'
            )

        temp_filepath = None
        with tempfile.NamedTemporaryFile(dir=self._temp_path, mode="wb", delete=False) as _file:
            temp_filepath = _file.name
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    break
                _file.write(chunk)

        hashes = {
            'content-md5': self.filehash(temp_filepath, hashlib.md5()),
            'content-sha1': self.filehash(temp_filepath, hashlib.sha1()),
            'content-sha256': self.filehash(temp_filepath, hashlib.sha256())        
        }

        if self.validate(temp_filepath, hashes):
            self._metadata.update(hashes)

            self.object_id = self._metadata[self.OBJECT_KEY_BASE]

            if hashes[self.OBJECT_KEY_BASE] not in self._objects_metadata:
                movefile(temp_filepath, self.filepath)
                self.metadata = self._metadata
            else:
                os.remove(temp_filepath)
                raise falcon.HTTPConflict(
                    title="ObjectAlreadyExists",
                    description="The object already exists into the storage.",
                    headers={
                        'content-md5':  self.metadata['content-md5'],
                        'content-sha1': self.metadata['content-sha1'],
                        'content-sha256': self.metadata['content-sha256'],
                    }
                )


    def filehash(self, filepath, hashfunc):
        ''' returns file hash
        '''
        block_size = 2 ** 20
        with open(filepath, 'rb') as _file:
            while True:
                data = _file.read(block_size)
                if not data:
                    break
                hashfunc.update(data)
        return hashfunc.hexdigest()


    def validate(self, filepath, filehashes):
        ''' validate recieved file object
        '''
        if os.path.getsize(filepath) == 0:
            os.remove(filepath)
            raise falcon.HTTPBadRequest(
                title='ZeroContentLength',
                description='The content size is 0'
            )

        if 'content-length' in self._metadata and \
            os.path.getsize(filepath) != self._metadata['content-length']:
            os.remove(filepath)
            raise falcon.HTTPBadRequest(
                title='BadContentLength',
                description='The Content-length did not match'
            )

        if 'content-md5' in self._metadata and \
            filehashes['md5'] != self._metadata['content-md5']:
            os.remove(filepath)
            raise falcon.HTTPBadRequest(
                title='BadDigest',
                description='The Content-MD5 did not match'
            )

        if 'content-sha1' in self._metadata and \
            filehashes['sha1'] != self._metadata['content-sha1']:
            os.remove(filepath)
            raise falcon.HTTPBadRequest(
                title='BadDigest',
                description='The Content-SHA1 did not match'
            )

        return True

    def delete(self):
        ''' delete object
        '''
        if self.exists():
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            else:
                raise falcon.HTTPNotFound()
            self._objects_metadata.pop(self.object_id)


    def info(self):
        ''' returns object's metadata
        '''
        if self.object_id and self.object_id in self._objects_metadata:
            return self._objects_metadata[self.object_id]
        else:
            return self._metadata

