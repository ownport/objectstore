# -*- coding: utf-8 -*-

import os
import json
import shutil
import tempfile

import falcon
import falcon.testing as testing

from objectstore.api import service
from objectstore.api import buckets


class TestObjectStoreBucketCollection(testing.TestBase):

    def before(self):

        self.storage_path = tempfile.mkdtemp(dir='/tmp/')
        self.api.add_route('/bucket', buckets.BucketCollectionAPI(storage_path=self.storage_path))


    def after(self):

        shutil.rmtree(self.storage_path)


    def test_bucket_collection_options(self):

        body = self.simulate_request('/bucket', method='OPTIONS')
        self.assertEqual(self.srmock.headers, [('allow', 'PUT')])
        self.assertEqual(self.srmock.status, falcon.HTTP_204)



    def test_create_new_bucket(self):

        body = self.simulate_request('/bucket', method='PUT', query_string='name=test1')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(
            [json.loads(e) for e in body], 
            [{
                'name':'test1'
            }]
        )


    def test_create_new_bucket_missing_name_param(self):

        body = self.simulate_request('/bucket', method='PUT')
        self.assertEqual(self.srmock.status, falcon.HTTP_400)
        self.assertEqual(
            [json.loads(e) for e in body], 
            [{
                u'description': u'The "name" parameter is required.',
                u'title': u'Missing parameter'
            }]
        )


    def test_create_new_bucket_with_incorrect_name(self):

        body = self.simulate_request('/bucket', method='PUT', query_string='name=test#1')
        self.assertEqual(self.srmock.status, falcon.HTTP_400)


    def test_create_bucket_if_exists(self):

        body = self.simulate_request('/bucket', method='PUT', query_string='name=bucket-exists')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/bucket', method='PUT', query_string='name=bucket-exists')
        self.assertEqual(self.srmock.status, falcon.HTTP_409)
        self.assertEqual(
            [json.loads(e) for e in body], 
            [{
                u'description': u'The requested bucket name \'bucket-exists\' is not available. Please select a different name and try again.',
                u'title': u'BucketAlreadyExists'
            }]
        )




class TestObjectStoreIncorrectStoragePath(testing.TestBase):

    def before(self):

        self.storage_path = tempfile.mkdtemp(dir='/tmp/')
        self.api.add_route('/bucket', buckets.BucketCollectionAPI(storage_path=self.storage_path))
        self.api.add_route('/bucket/{bucket_name}', buckets.BucketAPI(storage_path=self.storage_path))


    def test_incorrect_storage_path(self):

        body = self.simulate_request('/bucket', method='PUT', query_string='name=incorrect-storage-path')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        shutil.rmtree(self.storage_path)

        body = self.simulate_request('/bucket/incorrect-storage-path', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_500)



class TestObjectStoreBucket(testing.TestBase):

    def before(self):

        self.storage_path = tempfile.mkdtemp(dir='/tmp/')
        self.api.add_route('/bucket', buckets.BucketCollectionAPI(storage_path=self.storage_path))
        self.api.add_route('/bucket/{bucket_name}', buckets.BucketAPI(storage_path=self.storage_path))


    def after(self):

        shutil.rmtree(self.storage_path)


    def test_bucket_options(self):

        body = self.simulate_request('/bucket/test1', method='OPTIONS')
        self.assertEqual(self.srmock.headers, [('allow', 'DELETE, GET, HEAD')])
        self.assertEqual(self.srmock.status, falcon.HTTP_204)


    def test_check_non_exists_bucket(self):

        body = self.simulate_request('/bucket/non-exists', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_404)


    def test_check_exists_bucket(self):

        body = self.simulate_request('/bucket', method='PUT', query_string='name=exists')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/bucket/exists', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)


    def test_delete_bucket(self):

        body = self.simulate_request('/bucket', method='PUT', query_string='name=for-delete')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/bucket/for-delete', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/bucket/for-delete', method='DELETE')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/bucket/for-delete', method='HEAD')
        self.assertEqual(self.srmock.status, falcon.HTTP_404)


    def test_delete_non_exists_bucket(self):

        body = self.simulate_request('/bucket/non-exists', method='DELETE')
        self.assertEqual(self.srmock.status, falcon.HTTP_404)


    def test_objects_list(self):

        body = self.simulate_request('/bucket', method='PUT', query_string='name=with-objects')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)

        body = self.simulate_request('/bucket/with-objects', method='GET')
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(
            [json.loads(e) for e in body], 
            [{u'objects': [], u'metadata': {u'name': u'with-objects'}}]
        )


    def test_objects_list_non_exists_bucket(self):

        body = self.simulate_request('/bucket/not-exists', method='GET')
        self.assertEqual(self.srmock.status, falcon.HTTP_404)




