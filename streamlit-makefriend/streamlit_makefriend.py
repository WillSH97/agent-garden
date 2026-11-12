import streamlit as st
import requests
import json

import os

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://localhost:8000")

with st.form("make a friend!", clear_on_submit = False):
    name = st.text_input("Enter your friend's name")
    likes = st.text_input("list what they like")
    dislikes = st.text_input("list what they dislike")
    personality = st.text_input("describe their personality")
    
    submitted = st.form_submit_button("Submit")

    if submitted:
        response = requests.get(url = FASTAPI_URL+"/friendlist")
        response.raise_for_status() # creates error if there's sth wrong
        friendlist = response.json()
        if not name.strip() or not likes.strip() or not dislikes.strip() or not personality.strip(): #it's 10pm don't look at me
            st.warning("fill out all traits!")
        elif name in friendlist:
            st.warning("that friend (or their name) already exists!")
        else:
            #TODO: add function here that submits to make friend
            payload = {
                "likes": likes,
                "dislikes": dislikes, 
                "personality": personality,
                "name": name
            }
            response = requests.post(url = FASTAPI_URL+"/makefriend", json = payload)
            response.raise_for_status()
            st.success("you've made a friend!")
            # st.rerun()