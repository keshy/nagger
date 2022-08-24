import streamlit as st
from google.cloud import storage
import json
from streamlit_tags import st_tags
import user_mgmt


class StorageClient:
    BUCKET_NAME = "digisafe-nagger"
    PWD_FILE_NAME_FORMAT = "%s/pwd_config.json"

    def __init__(self):
        self._storage_client = None

    def get_client(self):
        if not self._storage_client:
            self._storage_client = storage.Client()
        return self._storage_client


class Pwd:
    PASS_KEY = "brindavanam"

    def __init__(self):
        self.item_id = None
        self.url = None
        self.desc = None
        self.updated_at = None
        self.username = None
        self.pwd = None
        self.secondary_pwd = []
        self.labels = []

    def to_json(self):
        return json.dumps(self.__dict__)


class PwdMgr:
    def __init__(self, user=None):
        self.storage_client = StorageClient()
        self._cache = None
        self.user = user

    def _lazy_init_storage_client(self):
        return self.storage_client.get_client()

    def validate_config(self):
        if not self.user:
            raise Exception("User state not valid")

    def _refresh_cache(self):
        # load from source
        try:
            bucket = self._lazy_init_storage_client().bucket(StorageClient.BUCKET_NAME)
            blob = bucket.blob((StorageClient.PWD_FILE_NAME_FORMAT % self.user))
            content = blob.download_as_string()
            self._cache = json.loads(content)
        except Exception as e:
            raise e

    def list_pwds(self):
        self.validate_config()
        if self._cache is None:
            self._refresh_cache()
        return self._cache

    def add_or_update_pwds(self, pwds):
        if not self._cache:
            self._refresh_cache()
        cpy = self._cache.copy()
        cpy[pwds.item_id] = pwds.__dict__
        try:
            bucket = self._lazy_init_storage_client().bucket(StorageClient.BUCKET_NAME)
            blob = bucket.blob((StorageClient.PWD_FILE_NAME_FORMAT % self.user))
            blob.upload_from_string(json.dumps(cpy))
        except Exception as e:
            raise e
        self._cache = cpy
        print('completed updating remote and local data with cache ')

    def delete(self, item_ids=None):
        if not self._cache:
            self._refresh_cache()
        cpy = self._cache.copy()
        for item in item_ids:
            cpy.pop(item)
        try:
            bucket = self._lazy_init_storage_client().bucket(StorageClient.BUCKET_NAME)
            blob = bucket.blob((StorageClient.PWD_FILE_NAME_FORMAT % self.user))
            blob.upload_from_string(json.dumps(cpy))
        except Exception as e:
            raise e
        self._cache = cpy
        print('completed removing keys %s for user %s ' % (item_ids, self.user))

    def enable_pwd_mgr(self):
        print("Inside enable pwd mgr")
        try:
            bucket = self._lazy_init_storage_client().bucket(StorageClient.BUCKET_NAME)
            blob = bucket.blob((StorageClient.PWD_FILE_NAME_FORMAT % self.user))
            blob.upload_from_string(json.dumps({}))
        except Exception as e:
            raise e
        self._cache = {}


st.title("Password Manager")
st.write("""
    Password Manager can be used to browse and remotely update passwords for various accounts from any device.
    The password is stored in encrypted format and is never going to leave the intranet. 
""")


def add_presentation_layer_for_users(o_user, f_user, u_mgr):
    with st.expander(o_user):
        pwd_list = None
        try:
            pwd_list = u_mgr.list_pwds()
        except Exception as e:
            print(e)
            st.button(key=f_user + "_enabler_btn", label="Enable", on_click=u_mgr.enable_pwd_mgr)
        if pwd_list is not None:
            st.json(pwd_list)
            st.write("Look up Password by Item Id")

            selection = st.multiselect(key=f_user + "_pwd_ms", label="Select Password Item",
                                       options=u_mgr.list_pwds().keys())
            res = {}
            for x in selection:
                res[x] = u_mgr.list_pwds().get(x)
            st.json(res)
            st.write("Search passwords by labels")
            lbls = set()
            lbl_to_id_map = {}
            for x, v in u_mgr.list_pwds().items():
                for i in v.get('labels'):
                    lbls.add(i)
                    lbl_to_id_map[i] = x
            labels = st.multiselect(key=f_user + "_pwd_label_ms", label="Select Labels to filter",
                                    options=lbls)
            result = {}
            for x in labels:
                result[lbl_to_id_map[x]] = u_mgr.list_pwds().get(lbl_to_id_map[x])
            st.json(result)

            st.write("Add/update new password")
            p = Pwd()
            p.item_id = st.text_input(key=f_user + "_item_id", label="Item Id*")
            p.url = st.text_input(key=f_user + "_url", label="URL*")
            p.desc = st.text_input(key=f_user + "_description", label="Description")
            p.username = st.text_input(key=f_user + "_username", label="Username")
            p.pwd = st.text_input(key=f_user + "_password", label="Password", type="password")
            p.labels = st_tags(key=f_user + "_tags", label="Labels", maxtags=5)
            st.button(key=f_user + "_submit_btn", label="Submit", on_click=u_mgr.add_or_update_pwds, args=(p,))
            st.write("Delete Password")
            del_items = st.multiselect(key=f_user + '_del_ms', label="Items to be deleted",
                                       options=u_mgr.list_pwds().keys())
            del_json = {}
            for x in del_items:
                del_json[x] = u_mgr.list_pwds().get(x)
            st.json(del_json)
            st.button(key=f_user + "_del_btn", label="Delete", on_click=u_mgr.delete, args=(del_items,))


u_to_mgr_map = {}
us = user_mgmt.get_user_mgr()

if not us.list():
    st.error("No users are registered or eligible. Please add users in the Users page to use this feature")

for u in us.list():
    u_to_mgr_map[u.lower()] = PwdMgr(u.lower())

for u in us.list():
    add_presentation_layer_for_users(u, u.lower(), u_to_mgr_map.get(u.lower()))
