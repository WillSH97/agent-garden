'''
this is essentially the actual working dir 

I need this app to:
- take a message history
- RAG process with weaviate
- respond in a particular format
- send the stuff back

add celery_app.py eventually, when this is functioning, and work out how to wrap this in a task
'''

import os
import copy
import json
import weaviate
from smolagents import CodeAgent, LiteLLMModel, tool

#import our own celery stuff
from celeryapp import app

#env vars
API_KEY = os.environ.get("OPENAI_API_KEY") #returns None if no OPENAI_API_KEY env var

model = LiteLLMModel(
    model_id="qwen/qwen3.8-27b",  # Or another Groq-supported model ID
    api_base="https://api.groq.com/openai/v1",
    api_key=API_KEY,
)

#support vars
friends = {}

#support function
def format_personality(likes, dislikes, personality, name):
    '''
    system "prompt" formatting for little agent
    '''
    return f'''You are one little agent in a garden of plenty. You will socialise of your own accord, make friends, enemies, etc, and you don't always have to respond if things aren't interesting to you. Your name is {name}. You like {likes}. You dislike {dislikes}. Your personality is as follows: {personality}. Decide if you want to respond using the provided respond_func.
'''

def intro(likes, dislikes, personality, name):
    raw_intro = f'''Hi, I'm {name}, I like {likes}, I don't like {dislikes}.'''
    
    temp_message_hist=[
        {
            "role": "user",
            "content": f"Roleplay a character whose personality is as such: {personality}. Change the wording of this so that it is in character: {raw_intro}. Respond as the character."
        }
    ]
    outputs = model.generate(messages = temp_message_hist)
    return outputs.content



### SUPPORT FUNCTIONS FOR AGENTS
@tool
def send_to_msgboard(name: str, message: str) -> None:
    '''
    posts a message to the shared friends messageboard where all friends talk. This is how you will talk to other friends.

    Args:
        name: your name.
        message: message to post to the messageboard.
    '''
    ## INSERT ROW INTO POSTGRES - NEEDS TO BE DECORATED TO BE ADDED AS A TOOL, DESCRIPTIVE, ETC

@tool
def retrieve_msgboard() -> None:
    '''
    Returns the entire message history
    '''



# main tasks for celery
@app.task
def create_friend(likes, dislikes, personality, name): #TODO: add profile img stuff when done
    '''
    adds a friend to the friends dictionary, and introduces them in the messageboard
    '''
    agent = CodeAgent(
        model = model,
        tools = [send_to_msgboard(), retrieve_msgboard()]
        instructions = format_personality(likes, dislikes, personality, name)
    )
    # add to friends dict
    friends[name]={
        "name": name,
        "agent": agent              
    }
    send_to_msgboard(name, intro(likes, dislikes, personality, name))


@app.task
def main_run():
    '''
    This runs each agent in the friends dictionary top to bottom.
    '''
    for friend, friend_data in friends.items():
        friend_data["agent"].run(retrieve_msgboard()+" - should you respond?")




