import os
import re
import json

from fastapi import UploadFile
from bson.json_util import dumps
from bson.objectid import ObjectId
from fastapi import APIRouter, Form, File, Request, HTTPException

from la_api.db_utils import DBClient


db_client = DBClient()

router = APIRouter(
    prefix="/sponsors",
    tags=["sponsors"],
    responses={404: {"description": "Not found"}}
)


collection = db_client.db.survey


@router.get("/")
async def get_all():
    return json.loads(dumps(collection.find()))


@router.get("/{id}")
async def get_by_(id: str):
    return json.loads(dumps(collection.find({"_id": ObjectId(id)})))


@router.post("/")
async def add_sponsor(name: str = Form(...), website: str = Form(...), picture: UploadFile = File(...)):
    sponsor = {
        "picture": picture.file.read(),
        "name": name,
        "website": website
    }
    new_member = collection.insert_one(sponsor).inserted_id
    return json.loads(dumps(new_member))
