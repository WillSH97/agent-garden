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
def RAGchat(friend_stats: MakeFriend):
# Send task by name
    celery_app.send_task('tasks.create_friend', args=[friend_stats.likes, friend_stats.dislikes, friend_stats.personality, friend_stats.name,])
    # TODO: add robustness by returning descriptive stuff in case there's issues here


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)