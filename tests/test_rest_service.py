# -*- coding: utf-8 -*-

import json
import shutil
import tempfile

import falcon
import falcon.testing as testing

from objectstore.api import service
from objectstore.api import buckets


class TestObjectStoreService(testing.TestBase):

    def before(self):

        self.storage_path = tempfile.mkdtemp(dir='/tmp/')
        self.api.add_route('/service', service.ServiceAPI(storage_path=self.storage_path))
        self.api.add_route('/bucket', buckets.BucketCollectionAPI(storage_path=self.storage_path))


    def after(self):

        shutil.rmtree(self.storage_path)


    def test_service_ok(self):

        body = self.simulate_request('/service', method='GET', decode='utf-8')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(body, u'{"buckets": []}')


    def test_service_buckets_list(self):

        body = self.simulate_request('/bucket', method='PUT', query_string='name=bucket-list-01')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        body = self.simulate_request('/bucket', method='PUT', query_string='name=bucket-list-02')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/service', method='GET')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(
            [json.loads(e) for e in body],
            [{"buckets": [{"name": "bucket-list-02"}, {"name": "bucket-list-01"}]}]
        )


    def test_service_storage_path_is_not_defined(self):

        self.api = falcon.API()
        with self.assertRaises(RuntimeError):
            self.api.add_route('/service', service.ServiceAPI(storage_path=None))


