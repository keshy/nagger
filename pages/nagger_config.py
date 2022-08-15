import pandas as pd
import streamlit as st
from google.cloud import storage
import json
import users

CONFIG_CACHE = {}
storage_client = None


def form_submit_callback(user=None, data=()):
    print("Made update to backend with data" + str(data))
    pass


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
        st.write("Add or update config")
        nagger_id = st.text_input(key=f_user + '_nagger_id', label="Item Id")
        due = st.date_input(key=f_user + '_due', label="Due Date")
        renewal = st.date_input(key=f_user + '_renewal', label="Renewal Date")
        ap = st.checkbox(key=f_user + '_chkbox', label='Auto Pay Enabled?')
        desc = st.text_input(key=f_user + '_desc', label="Description")
        due_cadence = st.multiselect(key=f_user + '_ms', label='cadence',
                                     options=['Monthly', 'Semi-Yearly', 'Yearly', 'Weekly'])
        st.button(key=f_user + '_submit_btn', label='Submit', on_click=form_submit_callback,
                  args=(f_user, (nagger_id, due, renewal, ap, desc, due_cadence)))
        st.write("Current Config")
        code_payload = CONFIG_CACHE.get(f_user)
        if not CONFIG_CACHE.get(f_user):
            status, msg = get_blob(f_user)
            code_payload = {} if status != 0 else CONFIG_CACHE.get(f_user)
        st.table(data=pd.DataFrame.from_dict(code_payload, orient="index"))


for u in users.USERS:
    add_configs_for_user(u, u.lower())

if __name__ == "__main__":
    get_blob("shankar")
