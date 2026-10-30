import streamlit as st
import time
import os
from celery import Celery
import psycopg2

REDIS_BROKER=os.environ.get("REDIS_BROKER")
REDIS_BACKEND=os.environ.get("REDIS_BACKEND")
print(REDIS_BROKER)
print(REDIS_BACKEND)

celery_app = Celery('worker', broker=REDIS_BROKER, backend=REDIS_BACKEND)

#support func
def return_messages():
    '''
    check the postgres and return all, formatted as message history
    '''
    conn = psycopg2.connect(    
        host="db",                     # Matches the docker-compose service name
        database="test",
        user="myuser",
        password="mypassword",
        port="5432"
    )
    cur = conn.cursor()
    return_msgboard_query ='''
SELECT name, message, personality from public.msgboard
'''
    results = cur.execute(return_msgboard_query)
    return_list = []
    for result in cur.fetchall():
        return_list.append(
            {
                "name": result[0],
                "message": result[1],
                "personality": result[2]
            }
        )

    cur.close()
    conn.close()
    return return_list

def clear_message_hist():
    '''
    clears all messages
    '''
    conn = psycopg2.connect(    
        host="db",                     # Matches the docker-compose service name
        database="test",
        user="myuser",
        password="mypassword",
        port="5432"
    )
    cur = conn.cursor()
    return_msgboard_query ='''
delete from public.msgboard
'''
    cur.execute(return_msgboard_query)
    cur.commit()
    cur.close()
    conn.close()



if "messages" not in st.session_state:
    st.session_state['messages'] = []

if "timer" not in st.session_state:
    st.session_state['timer'] = 0

for message in st.session_state['messages']:
    with st.chat_message(message["name"], ): #using the name par for the username, add avatar here
        st.title(f':small[{message["name"]}]', help=message["personality"])
        st.markdown(message["message"])

with st.sidebar:
    if st.button("delete chat history"):
        clear_message_hist()
        cand_msgs = return_messages()
        st.session_state['messages'] = cand_msgs
        st.rerun()



#shitty daemon process:
@st.fragment(run_every=5.0)
def check_updates():
    cand_msgs = return_messages()
    if cand_msgs != st.session_state['messages']:
        celery_app.send_task("tasks.main_run", args=[])
        st.session_state['messages'] = cand_msgs
        st.session_state['timer'] = 0 #set timer back to 0
        st.rerun()
    elif st.session_state['timer'] >= 90: #only rerun every 90 seconds of inactivity
        celery_app.send_task("tasks.main_run", args=[])
        st.session_state['timer'] = 0
    else:
        st.session_state['timer'] += 5 #increment timer another 5 seconds

check_updates()
    