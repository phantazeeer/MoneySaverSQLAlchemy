import os

import uvicorn
import yaml

from app import create_app

app = create_app()

path_to_execute = os.path.dirname(os.path.abspath(__file__))
log_config = yaml.safe_load(path_to_execute + "/log_config.yaml")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_config=log_config)
