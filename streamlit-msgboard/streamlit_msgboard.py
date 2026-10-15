import streamlit as st
import time

#support func
def return_messages():
    '''
    check the postgres and return all, formatted as message history
    '''

if "messages" not in st.session_state:
    st.session_state['messages'] = []

for message in st.session_state['messages']:
    with st.chat_message(message["name"], ): #using the name par for the username, add avatar here
        st.markdown(message["message"])

#shitty daemon process:
@st.fragment(run_every=5.0)
def check_updates():
    cand_msgs = return_messages()
    if cand_msgs != st.session_state['messages']:
        st.session_state['messages'] = cand_msgs
        st.rerun()
    # TODO: add logic here for sending requests for full agent reruns, make it do either every new msg, OR every 90s of inactivity

check_updates()
    