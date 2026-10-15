from celery import Celery
import os

#env vars
REDIS_BROKER=os.environ.get("REDIS_BROKER")
REDIS_BACKEND=os.environ.get("REDIS_BACKEND")

app = Celery('worker',
             broker=REDIS_BROKER,
             backend=REDIS_BACKEND,
             include=['tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()