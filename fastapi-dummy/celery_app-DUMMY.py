'''
NOTE: dummy file for now - has pattern for sending and retrieving tasks. Will add app scripts soon
'''
## to retrieve:
from celery import Celery

app = Celery('my_app', broker='redis://localhost:6379/0', backend='redis://localhost:6379/1')

# Send task by name
result = app.send_task('tasks.add', args=[2, 2])

# Wait for and retrieve the return value (blocking)
output = result.get()
print(output) 