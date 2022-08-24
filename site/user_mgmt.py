import json

from google.api_core.exceptions import NotFound
from google.cloud import storage

USER_MGR = None


class Users:
    BUCKET_NAME = "digisafe-nagger"

    def __init__(self):
        self.users = None
        self.client = storage.Client()

    def _refresh(self):
        content = None
        try:
            bucket = self.client.bucket(self.BUCKET_NAME)
            blob = bucket.blob("/user_list.json")
            content = blob.download_as_string()
        except NotFound:
            print("Uninitiated flow. First time set up")
            content = json.dumps([])
        except Exception as e:
            raise e
        self.users = json.loads(content)

    def add_all(self, usernames=[]):
        for u in usernames:
            self.add(u)

    def add(self, username=None):
        print("Got username as %s" % username)
        if username is None or username == '':
            return
        if self.users is None:
            self._refresh()
        cpy = self.users.copy()
        cpy.append(username)
        try:
            bucket = self.client.bucket(self.BUCKET_NAME)
            blob = bucket.blob("/user_list.json")
            blob.upload_from_string(json.dumps(cpy))
        except Exception as e:
            raise e
        self.users = cpy
        print('completed updating remote and local data with cache ')

    def list(self):
        if self.users is None:
            self._refresh()
        return self.users

    def delete_all(self, usernames=[]):
        for u in usernames:
            self.delete(u)

    def delete(self, username):
        if username is None or username == '':
            return
        if self.users is None:
            self._refresh()
        cpy = self.users.copy()
        idx = -1
        for i in range(0, len(cpy)):
            if cpy[i] == username:
                idx = i
        if idx > -1:
            cpy.pop(idx)
        try:
            bucket = self.client.bucket(self.BUCKET_NAME)
            blob = bucket.blob("/user_list.json")
            blob.upload_from_string(json.dumps(cpy))
        except Exception as e:
            raise e
        self.users = cpy
        print('completed updating remote and local data with cache ')


# Singleton
def get_user_mgr():
    global USER_MGR
    if not USER_MGR:
        USER_MGR = Users()
    return USER_MGR
