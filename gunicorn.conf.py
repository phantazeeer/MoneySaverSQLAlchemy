# gunicorn.conf.py
import os
from uvicorn.workers import UvicornWorker

LOG_LEVEL = os.getenv("LOG_LEVEL")


class MyUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "log_config": os.getenv("LOG_CONFIG", "./log_config.yaml"),
        "log_level": LOG_LEVEL
    }


bind = "0.0.0.0:8000"
workers = 9
worker_class = MyUvicornWorker
timeout = 180
graceful_timeout = 250
