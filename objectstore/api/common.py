import os

class BaseAPI(object):

    def __init__(self, storage_path):

        self._storage_path = None
        if storage_path and os.path.exists(storage_path):
            self._storage_path = storage_path
        else:
            raise RuntimeError('The storage path is not configured, "%s"' % storage_path)

