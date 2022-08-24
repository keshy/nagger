import streamlit as st
import user_mgmt

st.title("DigiSafe User Management")
st.write("Manage your users here. All users added here will be eligible for features available in Digisafe")
st.markdown("""
    #### User List 
""")
u = user_mgmt.get_user_mgr()
for i in u.list():
    st.markdown("""
        - %s
    """ % i)
st.markdown("""
    ---
""")
st.markdown("""
    #### Add User 
""")
username = st.text_input(key='user_input', label="Username*")
clicked = st.button(key='submit-btn', label='Submit', on_click=u.add, args=(username,))
if clicked and username is not None or username is not []:
    st.write("User %s will be added..." % username)
st.markdown("""
    ---
""")
st.markdown("""
    #### Delete User 
""")
d_username = st.multiselect(key='user_del_input', label="Username*", options=u.list())
del_clicked = st.button(key='del-submit-btn', label='Submit', on_click=u.delete_all, args=(d_username,))
if del_clicked and d_username is not None or d_username is not []:
    st.write("User %s will be deleted..." % d_username)
