# -*- coding: utf-8 -*-

import json
import falcon

from objectstore.api import service

from test_objectstore import ObjectStoreTestBase


class TestObjectStoreService(ObjectStoreTestBase):

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

        result = [json.loads(e) for e in body]
        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 1)

        buckets_list = result[0][u"buckets"]
        self.assertEqual(
            [b[u"name"] for b in buckets_list].sort(), 
            [u"bucket-list-01",u"bucket-list-02"].sort()
        )


    def test_service_storage_path_is_not_defined(self):

        self.api = falcon.API()
        with self.assertRaises(RuntimeError):
            self.api.add_route('/service', service.ServiceAPI(storage_path=None))


