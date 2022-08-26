from google.api_core.exceptions import NotFound
from google.cloud import storage
import json
import config

DOC_MGR = None


class Docs:
    def __init__(self):
        self.docs = None
        self.client = storage.Client()
        self.config = config.get_config_mgr()

    def _refresh(self):
        content = None
        try:
            bucket = self.client.bucket(self.config.get_bucket())
            blob = bucket.blob("/doc_list.json")
            content = blob.download_as_string()
        except NotFound:
            content = json.dumps([])
        except Exception as e:
            raise e
        self.docs = json.loads(content)

    def add(self, doc=None):
        if doc is None or doc == '':
            return
        if self.docs is None:
            self._refresh()
        cpy = self.docs.copy()
        cpy.append(doc)
        try:
            bucket = self.client.bucket(self.config.get_bucket())
            blob = bucket.blob("/doc_list.json")
            blob.upload_from_string(json.dumps(cpy))
        except Exception as e:
            raise e
        self.docs = cpy
        print('completed updating remote and local data with cache ')

    def list(self):
        if self.docs is None:
            self._refresh()
        return self.docs

    def delete_all(self, docs=[]):
        for u in docs:
            self.delete(u)

    def delete(self, doc):
        if doc is None or doc == '':
            return
        if self.docs is None:
            self._refresh()
        cpy = self.docs.copy()
        idx = -1
        for i in range(0, len(cpy)):
            if cpy[i][0] == doc:
                idx = i
        if idx > -1:
            cpy.pop(idx)
        try:
            bucket = self.client.bucket(self.config.get_bucket())
            blob = bucket.blob("/doc_list.json")
            blob.upload_from_string(json.dumps(cpy))
        except Exception as e:
            raise e
        self.docs = cpy
        print('completed updating remote and local data with cache ')


# Singleton
def get_doc_mgr():
    global DOC_MGR
    if not DOC_MGR:
        DOC_MGR = Docs()
    return DOC_MGR
