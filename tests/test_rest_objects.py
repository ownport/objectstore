# -*- coding: utf-8 -*-
import shutil
import tempfile

import falcon
import falcon.testing as testing

from objectstore.api import service
from objectstore.api import buckets
from objectstore.api import objects

class TestObjectStoreObject(testing.TestBase):

    def before(self):

        self.storage_path = tempfile.mkdtemp(dir='/tmp/')
        self.api.add_route('/bucket', buckets.BucketCollectionAPI(storage_path=self.storage_path))
        self.api.add_route('/bucket/{bucket_name}', buckets.BucketAPI(storage_path=self.storage_path))
        self.api.add_route('/bucket/{bucket_name}/object/{object_id}', objects.ObjectAPI(storage_path=self.storage_path))


    def after(self):

        shutil.rmtree(self.storage_path)


    def test_objects_options(self):

        body = self.simulate_request('/bucket/object-options/object/object-01', method='OPTIONS')
        self.assertEqual(self.srmock.headers, [('allow', 'DELETE, GET, HEAD, POST, PUT')])
        self.assertEqual(self.srmock.status, falcon.HTTP_204)


    def test_non_exist_object(self):

        body = self.simulate_request('/bucket/object-options/object/object-01', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_400)

