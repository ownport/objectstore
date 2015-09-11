# -*- coding: utf-8 -*-

import falcon

from objectstore.api import buckets

from test_objectstore import ObjectStoreTestBase



class TestBucket(ObjectStoreTestBase):


    def test_bucket_metadata(self):

        error_raised = False
        bucket = buckets.Bucket('metadata-check', storage_path=self.storage_path)
        try:
            bucket.metadata = None
        except RuntimeError:
            error_raised = True
        
        assert error_raised, 'Incorrect handling of metadata validation'


    def test_delete_bucket(self):

        bucket = buckets.Bucket('delete-check', storage_path=self.storage_path)
        self.assertRaises(falcon.HTTPNotFound, bucket.delete)


class TestBucketCollection(ObjectStoreTestBase):

    def test_incorrect_storage_path(self):

        self.assertRaises(falcon.HTTPInternalServerError, buckets.BucketCollection, storage_path='/123')
