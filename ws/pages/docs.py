import streamlit as st
import doc_mgmt

st.title("Document Manager")
st.write("Manage your docs here that's relevant for family")
st.markdown("""
    #### Document List 
""")
d = doc_mgmt.get_doc_mgr()
for i in d.list():
    k = i[0]
    v = i[1] if not None else ''
    st.markdown("""
        - [%s](%s)
    """ % (k, v))
st.markdown("""
    ---
""")
st.markdown("""
    #### Add Document 
""")
doc_name = st.text_input(key='doc_input', label="Document Name*")
doc_link = st.text_input(key='link_input', label="Link")
clicked = st.button(key='submit-btn', label='Submit', on_click=d.add, args=((doc_name, doc_link),))
st.markdown("""
    ---
""")
st.markdown("""
    #### Delete Document 
""")
d_username = st.multiselect(key='doc_del_input', label="Document Name*", options=[x[0] for x in d.list()])
del_clicked = st.button(key='del-submit-btn', label='Submit', on_click=d.delete_all, args=(d_username,))
