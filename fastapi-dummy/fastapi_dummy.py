'''
NOTE: dummy file for now - has pattern for sending and retrieving tasks. Will add app scripts soon
'''
## to retrieve:
from celery import Celery
import os

REDIS_BROKER=os.environ.get("REDIS_BROKER")
REDIS_BACKEND=os.environ.get("REDIS_BACKEND")
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2

celery_app = Celery('worker', broker=REDIS_BROKER, backend=REDIS_BACKEND)
app = FastAPI()

#typing
class MakeFriend(BaseModel):
    likes: str
    dislikes: str
    personality: str
    name: str



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/makefriend")
def makefriend(friend_stats: MakeFriend):
# Send task by name
    celery_app.send_task('tasks.create_friend', args=[friend_stats.likes, friend_stats.dislikes, friend_stats.personality, friend_stats.name,])
    # TODO: add robustness by returning descriptive stuff in case there's issues here

@app.get("/friendlist")
def friendlist() -> list:
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
SELECT DISTINCT name from public.msgboard
'''
    results = cur.execute(return_msgboard_query)
    return_list = [str(x[0]) for x in cur.fetchall()]
    cur.close()
    conn.close()
    return return_list


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)