import os
import random
import time

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

APP_VERSION = os.environ.get("APP_VERSION", "v1")
STARTED_AT = time.monotonic()

FAILURE_MODE = os.environ.get("FAILURE_MODE", "") == "1"

app = FastAPI()


@app.get("/")
def root():
    return {
        "app": "demo-api",
        "version": APP_VERSION,
        "hostname": os.uname().nodename,
    }


@app.get("/healthz")
def healthz():
    if FAILURE_MODE:
        return JSONResponse(status_code=500, content={"status": "failing (FAILURE_MODE=1)"})
    return {"status": "ok"}


@app.get("/version")
def version():
    return Response(content=APP_VERSION, media_type="text/plain")


@app.get("/work")
def work():
    time.sleep(random.uniform(0.8, 1.2))
    return {"version": APP_VERSION, "slept": "about 1s"}


@app.get("/uptime")
def uptime():
    return {"uptime_seconds": round(time.monotonic() - STARTED_AT, 1)}
