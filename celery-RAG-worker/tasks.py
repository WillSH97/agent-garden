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
from smolagents import CodeAgent, LiteLLMModel, tool, LogLevel
import psycopg2

#import our own celery stuff
from celeryapp import app

#env vars
API_KEY = os.environ.get("OPENAI_API_KEY") #returns None if no OPENAI_API_KEY env var

model = LiteLLMModel(
    model_id="qwen/qwen3.8-27b",  # Or another Groq-supported model ID
    api_base="https://api.groq.com/openai/v1",
    api_key=API_KEY,
)

# model = LiteLLMModel(
#     model_id="openai/lfm3-1.7b",  # Or another Groq-supported model ID
#     api_base="http://localhost:8081/v1",
#     api_key="none"
# )

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

def format_chat_hist(pg_chat_hist):
    return_str = 'WHOLE MESSAGE HISTORY - '
    for result in pg_chat_hist:
        return_str += f"[message no.: {result[0]}, message sender name: {result[1]}, message: {result[2]}], "
    return return_str

def basic_intro(likes, dislikes, personality, name):
    raw_intro = f'''name: {name}
    likes: {likes}
    dislikes: {dislikes}
    personality: {personality}'''
    return raw_intro
    
        



### SUPPORT FUNCTIONS FOR AGENTS
@tool
def send_to_msgboard(name: str, message: str) -> None:
    '''
    posts a message to the shared friends messageboard where all friends talk. This is how you will talk to other friends.

    Args:
        name: your name.
        message: message to post to the messageboard.
    '''
    conn = psycopg2.connect(    
        host="db",                     # Matches the docker-compose service name
        database="test",
        user="myuser",
        password="mypassword",
        port="5432"
    )
    cur = conn.cursor()
    create_table_query ='''
CREATE TABLE IF NOT EXISTS msgboard (
id SERIAL PRIMARY KEY,
name VARCHAR NOT NULL,
message VARCHAR NOT NULL,
personality VARCHAR NOT NULL
)
'''
# image VARCHAR NOT NULL
    cur.execute(create_table_query) #FIGURE OUT AT WHICH POINT THIS SHOULD RUN REALISTICALLY


    insert_query = """
INSERT INTO msgboard (name, message, personality) 
VALUES (%s, %s, %s);
    """
    msg_data = (name, message, friends[name]["personality"], ) # friends[name]["img"]
    cur.execute(insert_query, msg_data)
    conn.commit()
    # records = cur.fetchall()
    cur.close()
    conn.close()
    # return records

@tool
def retrieve_msgboard() -> str:
    '''
    Returns the entire message history of the messageboard of friends.
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
SELECT id, name, message from public.msgboard
'''
    results = cur.execute(return_msgboard_query)
    return_str = format_chat_hist(cur.fetchall())
    cur.close()
    conn.close()
    return return_str


# main tasks for celery
@app.task
def create_friend(likes, dislikes, personality, name): #TODO: add profile img stuff when done
    '''
    adds a friend to the friends dictionary, and introduces them in the messageboard
    '''
    agent = CodeAgent(
        model = model,
        tools = [send_to_msgboard, retrieve_msgboard],
        instructions = format_personality(likes, dislikes, personality, name),
        verbosity_level = LogLevel.INFO,
    )
    # add to friends dict
    friends[name]={
        "name": name,
        "agent": agent,
        "personality": basic_intro(likes, dislikes, personality, name),
        # "img": img
    }
    
    send_to_msgboard(name = name, message = intro(likes, dislikes, personality, name))


@app.task
def main_run():
    '''
    This runs each agent in the friends dictionary top to bottom.
    '''
    for friend, friend_data in friends.items():
        friend_data["agent"].run(retrieve_msgboard()+" - should you respond?")




