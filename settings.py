REDIS_ENDPOINT = "redis.example.com"
REDIS_PORT = 17579
REDIS_PASSWORD = "password"
POLL_INTERVAL = 10  # in seconds
TASK_KEY = "tasks"
MAX_TASK_ATTEMPTS = 20
GET_TASK_WAIT = 5
DO_SHUTDOWN = False
OUTFILES = []
RUN_NAME = 'run'

try:
    from local_settings import *
except ImportError:
    pass
