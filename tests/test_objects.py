# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

from objectstore.api import objects
from objectstore.api import buckets


class TestBucket(unittest.TestCase):

    def test_object_get_metadata_from_header(self):

        self.assertEqual(objects.get_metadata_from_headers({}), {})

        self.assertEqual(objects.get_metadata_from_headers({'CONTENT-LENGTH': 10}), {'content-length':10})
        self.assertRaises(ValueError, objects.get_metadata_from_headers, {'CONTENT-LENGTH': 'abc'})

        self.assertEqual(objects.get_metadata_from_headers({'CONTENT-MD5': '12312321'}), {'content-md5':'12312321'})

        self.assertEqual(objects.get_metadata_from_headers({'CONTENT-SHA1': '12312321'}), {'content-sha1':'12312321'})

        self.assertEqual(objects.get_metadata_from_headers({'CONTENT-TYPE': '12312321'}), {'content-type':'12312321'})


    def test_object_pairtree_path(self):

        self.assertRaises(RuntimeError, objects.pairtree_path, '')
        self.assertRaises(RuntimeError, objects.pairtree_path, '12')
        self.assertRaises(RuntimeError, objects.pairtree_path, '1234')

        self.assertEqual(objects.pairtree_path('1234567890'), '12/34/1234567890')
        self.assertEqual(objects.pairtree_path('1234567890', pairs=3), '12/34/56/1234567890')


    def test_object_movefile(self):

        try:
            handler, source = tempfile.mkstemp(dir='/tmp')
            tmp_path = tempfile.mkdtemp(dir='/tmp')
            target_dir = os.path.join(tmp_path, 'movefile/')

            objects.movefile(source, target_dir)
            self.assertTrue(
                os.path.exists( os.path.join(target_dir, os.path.basename(source)) )
            )

        finally:
            if os.path.exists(source):
                os.remove(source)

            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)


    def test_get_metadata(self):

        storage_path = tempfile.mkdtemp(dir='/tmp/')
        bucket = buckets.Bucket('b1', storage_path=storage_path)
        bucket.create()

        obj = objects.BucketObject('o1', bucket=bucket)
        self.assertEqual(obj.metadata, {})


