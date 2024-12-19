#!/usr/bin/env python3.11
from glob import glob
import json
import os
import time
from datetime import datetime, timedelta
import pathlib
import random
from fastapi import FastAPI, HTTPException, Path, Query, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import re
import uuid
import imageio.v3 as iio
import ssl
import uvicorn

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
    "https://mx-webapps.psi.ch",
    "https://heidi.psi.ch"
    "https://heidi-test.psi.ch",
    "https://heidi-sfx.psi.ch"
    # Add more allowed origins as needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

uuid4_re = re.compile(
    "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    re.IGNORECASE,
)

BASE_FOLDER = pathlib.Path("/images")

NUM_IDS = 0
try:
    with open("/data/tracking_ids.json") as fp:
        TRACKING_IDS = json.load(fp)
    NUM_IDS = len(TRACKING_IDS)
except:
    pass


def convert_tracking_id_to_path(tracking_id: str) -> pathlib.Path:
    """converts uuid4 tracking id string to path

    10c7c3d2-01a0-4596-9980-abd82423781e

    to

    PosixPath('10/c7/c3/d2/01/a0/45/96/99/80/ab/d8/24/23/78/1e')

    prefixes path with BASE_FOLDER

    """
    global BASE_FOLDER
    tracking_id = tracking_id.replace("-", "")
    parts = [tracking_id[n : n + 2] for n in range(0, len(tracking_id), 2)]
    _f = pathlib.Path(BASE_FOLDER, *parts)
    return _f


def find_one_image(fpath: pathlib.Path) -> pathlib.Path:
    """returns the first file in `fpath`

    raises FileNotFoundError if nothing found
    """
    try:
        image_filename = glob(f"{fpath}/*.*")[0]
    except:
        raise FileNotFoundError
    return pathlib.Path(image_filename)


class ImageResponse(Response):
    media_type = "image/*"


@app.get("/")
def root():
    return {"message": "MX Image Server"}


@app.get("/random", response_class=ImageResponse)
async def get_random_image():
    """returns a random image from the pool"""
    id = str(random.randint(0, NUM_IDS))
    entry = TRACKING_IDS[id]
    tracking_id = entry["tracking_id"]
    last_mod = get_last_modified_in_past()

    image_filename, ftype = get_imagepath_and_type(tracking_id)
    return FileResponse(
        image_filename,
        media_type=f"image/{ftype}",
        headers={"expires": "0", "Last-Modified": last_mod, "tracking-id": tracking_id},
    )


def get_last_modified_in_past() -> str:
    last_updated_pattern = "%a, %d %b %Y %H:%M:%S %Z"
    return time.strftime(
        last_updated_pattern, (datetime.now() - timedelta(hours=6)).timetuple()
    )


@app.get(
    "/image/{tracking_id}",
    response_class=ImageResponse,
)
async def get_image(
    tracking_id: Annotated[str, Path(title="An UUID4 string", max_length=37)]
):
    """fetches a microscope image for the corresponding tracking id

    `tracking_id` is a UUID4 conforming string

        UUID4 => 7874aa04-ee8e-43cb-a185-424205be4523

    """
    image_filename, ftype = get_imagepath_and_type(tracking_id)

    return FileResponse(image_filename, media_type=f"image/{ftype}")


def get_imagepath_and_type(tracking_id):
    image_folder = convert_tracking_id_to_path(tracking_id)
    try:
        image_filename = find_one_image(image_folder)
    except:
        image_filename = BASE_FOLDER / "oops-not-found.gif"

    ftype = image_filename.suffix.replace(".", "")
    return image_filename, ftype


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8443, log_level="info", ssl_context=ssl_context)
