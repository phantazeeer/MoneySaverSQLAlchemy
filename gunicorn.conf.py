# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 9
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 180
graceful_timeout = 250