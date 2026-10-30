import streamlit as st
import requests
import json

import os

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://localhost:8000")

with st.form("make a friend!"):
    name = st.text_input("Enter your friend's name")
    likes = st.text_input("list what they like")
    dislikes = st.text_input("list what they dislike")
    personality = st.text_input("describe their personality")
    
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not name.strip() or not likes.strip() or not dislikes.strip() or not personality.strip(): #it's 10pm don't look at me
            st.warning("fill out all traits!")
        else:
            #TODO: add function here that submits to make friend
            payload = {
                "likes": likes,
                "dislikes": dislikes, 
                "personality": personality,
                "name": name
            }
            requests.post(url = FASTAPI_URL+"/makefriend", json = payload)
            st.success("you've made a friend!")
            st.rerun()