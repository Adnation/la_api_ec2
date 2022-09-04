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
    prefix="/news",
    tags=["news"],
    responses={404: {"description": "Not found"}}
)


collection = db_client.db.news


@router.get("/")
async def get_all():
    return json.loads(dumps(collection.find()))


@router.get("/{id}")
async def get_by_(id: str):
    return json.loads(dumps(collection.find({"_id": ObjectId(id)})))


@router.post("/")
async def add_sponsor(headline: str = Form(...), date: str = Form(...), picture: UploadFile = File(...),
                      description: str = Form(...)):
    sponsor = {
        "headline": headline,
        "date": date,
        "picture": picture.file.read(),
        "description": description,
    }
    new_member = collection.insert_one(sponsor).inserted_id
    return json.loads(dumps(new_member))
