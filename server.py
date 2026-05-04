import os

import uvicorn
import yaml
from fastapi import HTTPException

from app import create_app
from app.db.database import check_db_connection

app = create_app()

path_to_execute = os.path.dirname(os.path.abspath(__file__))
log_config = yaml.safe_load(path_to_execute + "/log_config.yaml")


@app.get("/healthcheck/liveness", status_code=200, include_in_schema=False)
async def check_liveness():
    return {"detail": "OK"}


@app.get("/healthcheck/readiness", status_code=200, include_in_schema=False)
async def check_readiness():
    session = True if await check_db_connection() == 1 else False
    if session:
        return {"detail": "OK"}
    else:
        raise HTTPException(503, "No connection to database")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_config=log_config)
