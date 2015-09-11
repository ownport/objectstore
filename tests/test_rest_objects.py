# -*- coding: utf-8 -*-

import falcon

from test_objectstore import ObjectStoreTestBase


class TestObjectStoreObject(ObjectStoreTestBase):

    def test_objects_options(self):

        body = self.simulate_request('/bucket/object-options/object/object-01', method='OPTIONS')
        self.assertEqual(self.srmock.headers, [('allow', 'DELETE, GET, HEAD, POST, PUT')])
        self.assertEqual(self.srmock.status, falcon.HTTP_204)


    def test_non_exist_object(self):

        body = self.simulate_request('/bucket/object-options/object/object-01', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_400)

