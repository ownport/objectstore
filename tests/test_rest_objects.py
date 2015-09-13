# -*- coding: utf-8 -*-

import json
import falcon
import gunicorn

from test_objectstore import ObjectStoreTestBase


class TestObjectStoreObject(ObjectStoreTestBase):

    def before(self):

        super(TestObjectStoreObject, self).before()
        self.simulate_request('/bucket', method='PUT', query_string='name=test_objects')
        self.simulate_request('/bucket', method='PUT', query_string='name=test_objects_md5key&object-key=content-md5')


    def test_objects_options(self):

        body = self.simulate_request('/bucket/object-options/object/object-01', method='OPTIONS')
        self.assertEqual(self.srmock.headers, [('allow', 'DELETE, GET, HEAD, POST, PUT')])
        self.assertEqual(self.srmock.status, falcon.HTTP_204)


    def test_non_exist_bucket(self):

        body = self.simulate_request('/bucket/object-options/object/object-01', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_400)


    def test_non_exist_object(self):

        body = self.simulate_request('/bucket/test_objects/object/-e6fed90453a5dfe8ea1fb4088ef46b54cf7d7b77', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_404)        


    def test_put_object(self):

        body = self.simulate_request('/bucket/test_objects/object/put-object', method='PUT', body='###')
        self.assertEqual(
            [json.loads(e) for e in body], 
            [{
                u'content-name': u'put-object',
                u'content-length': 3,
                u'content-md5': u'dc27db9710c1c207a8bd46935163efc1',
                u'content-sha1': u'5c5b8251bdb4b62eff8c746f4021483bfae24eb7',
                u'content-sha256': u'56dc6d47737d155afddefda1af20c40c901353c222d01e70b7b4e021f2e4f548'
            }]
        )


    def test_put_object_with_object_key(self):

        body = self.simulate_request('/bucket/test_objects_md5key/object/put-object-with-object-key', method='PUT', body='1###')
        self.assertEqual(
            [json.loads(e) for e in body], 
            [{
                u'content-name': u'put-object-with-object-key',
                u'content-length': 4,
                u'content-md5': u'6c67e4f2aea14240a5a8c6303750d44d',
                u'content-sha1': u'9a2a678895eba59c691c2263ad69ab446652e5bc',
                u'content-sha256': u'70b3b94dff96d2b818ba8c3e522c8db463cca17fc238a604aa58f8682b314ae5'
            }]
        )


    def test_put_object_invalid_bucket_name(self):

        body = self.simulate_request('/bucket/no-bucket/object/put-object', method='PUT', body='###')
        self.assertEqual(
            [json.loads(e) for e in body], 
            [{
                u'description': u'The specified bucket is not valid',
                u'title': u'InvalidBucketName'
            }]
        )


    def test_put_exist_object(self):

        body = self.simulate_request('/bucket/test_objects/object/exist-object', method='PUT', body='####')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/bucket/test_objects/object/e6fed90453a5dfe8ea1fb4088ef46b54cf7d7b77', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual([json.loads(e) for e in body], [])
        self.assertEqual(
            dict(self.srmock.headers), 
            {
                u'content-name': u'exist-object',
                u'content-type': u'application/json; charset=utf-8',
                u'content-length': 4,
                u'content-md5': u'd9636b3388bd7b68bc02dc92c68ea328',
                u'content-sha1': u'e6fed90453a5dfe8ea1fb4088ef46b54cf7d7b77',
                u'content-sha256': u'c4a3b90d0d3210c35be2d9e93e9ed6810a037bdaba1aeccaa8498a8d5eddf1dc'
            }
        )


    def test_get_object(self):

        body = self.simulate_request(
            '/bucket/test_objects/object/get-object', 
            method='PUT', body='#####', headers={'Content-Type': 'text/plain'})
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/bucket/test_objects/object/c51d430a95691338da6a2455353eb0ab5fe08ef6', method='GET')
        self.assertEqual([e for e in body], ['#####',])
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(
            dict(self.srmock.headers), 
            {
                u'content-name': u'get-object',
                u'content-type': u'text/plain',
                u'content-length': u'5',
                u'content-md5': u'59fb38dbd2e7c8461be5422a4e12cacb',
                u'content-sha1': u'c51d430a95691338da6a2455353eb0ab5fe08ef6',
                u'content-sha256': u'9d56858ab62ca2d6de624b262a3d7b522403026982a01b6b4f82e46f0146ee51'
            }
        )

        body = self.simulate_request('/bucket/test_objects/object/-c51d430a95691338da6a2455353eb0ab5fe08ef6', method='GET')
        self.assertEqual(self.srmock.status, falcon.HTTP_404)        


    def test_delete_object(self):

        body = self.simulate_request(
            '/bucket/test_objects/object/delete-object', 
            method='PUT', body='delete-object', headers={'Content-Type': 'text/plain'})
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(
            [json.loads(e) for e in body], 
            [{
                u'content-name': u'delete-object',
                u'content-type': u'text/plain',
                u'content-length': 13,
                u'content-md5': u'7725bbca5cf2c8ce5e6ca03583978fe9',
                u'content-sha1': u'2f4461266997b1d288837f471890e3b2542c605f',
                u'content-sha256': u'8e67bd234e15ed0cd906aa3384ca3503b784aeccd53e0223d700f1aa6a07803e'
            }]
        )

        body = self.simulate_request('/bucket/test_objects/object/2f4461266997b1d288837f471890e3b2542c605f', method='DELETE')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/bucket/test_objects/object/2f4461266997b1d288837f471890e3b2542c605f', method='DELETE')
        self.assertEqual(self.srmock.status, falcon.HTTP_404)


