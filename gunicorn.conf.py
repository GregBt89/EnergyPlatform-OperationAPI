import os

bind = "{}:{}".format(os.environ['UVICORN_HOST'],
                      os.environ['UVICORN_PORT'])
workers = os.environ['UVICORN_WORKERS']

worker_class = "uvicorn.workers.UvicornWorker"