import streamlit as st
from PIL import Image
import user_mgmt
import config
import doc_mgmt

cfg_mgr = config.get_config_mgr()

st.title("Welcome to %s Intranet" % cfg_mgr.get_site_name())
st.write("""
    This ws would be used for locally managing all sensitive data, files, notifications/reminders etc. 
    No more uploading to gmail for everything for just passing files/data around within the house.  
""")
image = Image.open(cfg_mgr.get_picture())
st.image(image, caption='Manage digital asset spread across different places easily using one single solution!')
u, docs = st.columns(2)
us = user_mgmt.get_user_mgr()
doc = doc_mgmt.get_doc_mgr()

with u:
    st.markdown("""
        #### Family Members
         
    """)

    if not us.list():
        st.error("No users are registered or eligible. Please add users in the Users page to use this feature")

    for u in us.list():
        st.markdown("- %s" % u)

with docs:
    st.markdown("""
        #### Important Documents
    """)
    if not doc.list():
        st.error("No documents available for this ws. Please add them in Docs page")

    for d in doc.list():
        st.markdown('- [%s](%s)' % (d[0], d[1]))
