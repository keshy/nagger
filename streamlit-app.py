import streamlit as st
from pandas import DataFrame
from PIL import Image
import users

st.title("Welcome to Schoolhouse Intranet")
st.write("""
    This site would be used for locally managing all sensitive data, files, notifications/reminders etc. 
    No more uploading to gmail for everything for just passing files/data around within the house.  
""")
image = Image.open('family.jpg')
st.image(image, caption='Producers')

u, docs = st.columns(2)

with u:
    st.markdown("""
        #### Family Members
         
    """)
    for u in users.USERS:
        st.markdown("- %s" % u)

with docs:
    st.markdown("""
        #### Important Documents
        
        - [Property Management Upkeep](https://docs.google.com/spreadsheets/d/1f-U_s6A6LY_llyKqB7iSC2JGxWFxldoDgr9MBgxUwkc/edit#gid=0)
         
    """)
