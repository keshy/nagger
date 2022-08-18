import datetime
import streamlit as st
from google.cloud import storage
import json
import users

CONFIG_CACHE = {}
storage_client = None


def delete_item(user=None, nagger_id=[]):
    if not user:
        print("Error in submit - doing nothing")
        st.error("Data validation Error")
        return
    global CONFIG_CACHE
    cpy_on_update = CONFIG_CACHE.get(user)

    print('user - %s nagger_id - %s' % (user, nagger_id))
    for k in nagger_id:
        cpy_on_update.pop(k, None)
    try:
        global storage_client
        if not storage_client:
            storage_client = storage.Client()
        bucket = storage_client.bucket('digisafe-nagger')
        blob = bucket.blob(user + '/' + 'nagger_config.json')
        blob.upload_from_string(json.dumps(cpy_on_update))
    except Exception as e:
        print("Failed to remove items " + str(nagger_id) + ' for user ' + user + ' with reason: ' + str(e))
        return
    print("Completed updating remote storage for user " + user)
    CONFIG_CACHE[user] = cpy_on_update
    print('Completed updating local cache')


def form_submit_callback(user=None, nagger_id=None, data=None):
    if not nagger_id or not user:
        print("Error in submit - doing nothing")
        st.error("Data validation Error")
        return
    if data['description'] is None or (data['due'] is None and data['renewal'] is None):
        print("Invalid payload")
        st.error("Invalid input format")
        return

    global storage_client
    if not storage_client:
        storage_client = storage.Client()
    global CONFIG_CACHE
    cpy_on_update = CONFIG_CACHE.get(user)
    cpy_on_update[nagger_id] = data
    try:
        bucket = storage_client.bucket('digisafe-nagger')
        blob = bucket.blob(user + '/' + 'nagger_config.json')
        blob.upload_from_string(json.dumps(cpy_on_update))
    except Exception as e:
        print("Failed to update nagger item " + nagger_id + ' for user ' + user + ' with reason: ' + str(e))
        return
    print("Completed updating remote storage for user " + user)

    CONFIG_CACHE.get(user)[nagger_id] = data
    print('Completed updating local cache')


def get_blob(user=None):
    if not user:
        return 1, "Not a valid user"
    global storage_client
    try:
        if not storage_client:
            storage_client = storage.Client()
        bucket = storage_client.bucket('digisafe-nagger')
        blob = bucket.blob(user + '/' + 'nagger_config.json')
        contents = blob.download_as_string()
        global CONFIG_CACHE
        CONFIG_CACHE[user] = json.loads(contents)
        return 0, "success"
    except Exception as e:
        return 1, "Received exception to find nagger_config. Is this user registered? Contact keshi8086@gmail.com"


st.title("Nagger")
st.write(
    "Nagger is a smart reminder tool that will nag you about upcoming deadlines/dates that you need"
    " to complete some chore by. The system expects a configuration in a specified format to allow for periodic"
    " checks. The result of the checks will be sent to the provided email as a notification")


def add_configs_for_user(o_user, f_user):
    with st.expander(o_user):
        st.write("Current Config for " + f_user)
        code_payload = CONFIG_CACHE.get(f_user)
        if not CONFIG_CACHE.get(f_user):
            status, msg = get_blob(f_user)
            code_payload = {} if status != 0 else CONFIG_CACHE.get(f_user)
        if code_payload:
            st.json(code_payload)
            st.write("Add or update config")
            nagger_id = st.text_input(key=f_user + '_nagger_id', label="Item Id*")
            due = st.date_input(key=f_user + '_due', label="Due Date")
            renewal = st.date_input(key=f_user + '_renewal', label="Renewal Date", value=None)
            ap = st.checkbox(key=f_user + '_chkbox', label='Auto Pay Enabled?')
            desc = st.text_input(key=f_user + '_desc', label="Description*")
            due_cadence = st.multiselect(key=f_user + '_ms', label='cadence',
                                         options=['Monthly', 'Semi-Yearly', 'Yearly', 'Weekly'])
            st.button(key=f_user + "_submit_btn", label='Submit', on_click=form_submit_callback,
                      args=(f_user, nagger_id, {
                          "due": datetime.date.strftime(due, '%m/%d/%Y') if due else None,
                          "renewal": datetime.date.strftime(renewal, '%m/%d/%Y') if renewal else None,
                          "ap": ap,
                          "description": desc,
                          "cadence": due_cadence
                      }))
            st.write("Delete Config")
            keys = CONFIG_CACHE.get(f_user).keys()
            del_nagger_id = st.multiselect(key=f_user + '_delete_ms', label='Nagger ID*',
                                           options=keys)
            del_json = {}
            for x in del_nagger_id:
                del_json[x] = CONFIG_CACHE.get(f_user).get(x)
            st.json(del_json)
            st.button(key=f_user + "_del_btn", label='Submit', on_click=delete_item, args=(f_user, del_nagger_id))
        else:
            st.error(o_user + " is not registered for Nagger. Contact Keshi8086@gmail.com")


for u in users.USERS:
    add_configs_for_user(u, u.lower())

if __name__ == "__main__":
    get_blob("shankar")
