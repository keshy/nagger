import streamlit as st
from PIL import Image
import user_mgmt

st.title("Welcome to Schoolhouse Intranet")
st.write("""
    This site would be used for locally managing all sensitive data, files, notifications/reminders etc. 
    No more uploading to gmail for everything for just passing files/data around within the house.  
""")
image = Image.open('family_office.jpg')
st.image(image, caption='Producers')
u, docs = st.columns(2)
us = user_mgmt.get_user_mgr()

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
        
        - [Property Management Upkeep](https://docs.google.com/spreadsheets/d/1f-U_s6A6LY_llyKqB7iSC2JGxWFxldoDgr9MBgxUwkc/edit#gid=0)
         
    """)
