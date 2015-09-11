# -*- coding: utf-8 -*-

import shutil
import tempfile

import falcon.testing as testing

from objectstore.api import service
from objectstore.api import buckets
from objectstore.api import objects


class ObjectStoreTestBase(testing.TestBase):

    def before(self):

        self.storage_path = tempfile.mkdtemp(dir='/tmp/')
        self.api.add_route('/service', service.ServiceAPI(storage_path=self.storage_path))
        self.api.add_route('/bucket', buckets.BucketCollectionAPI(storage_path=self.storage_path))
        self.api.add_route('/bucket/{bucket_name}', buckets.BucketAPI(storage_path=self.storage_path))
        self.api.add_route('/bucket/{bucket_name}/object/{object_id}', objects.ObjectAPI(storage_path=self.storage_path))


    def after(self):

        self.remove_storage_path()


    def remove_storage_path(self):

        shutil.rmtree(self.storage_path, ignore_errors=True)



