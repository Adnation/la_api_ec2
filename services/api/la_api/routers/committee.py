import os
import json
import boto3

from fastapi import UploadFile
from bson.json_util import dumps
from bson.objectid import ObjectId
from fastapi import APIRouter, Form, File


from la_api.dynamo_utils import DynamoClient

dynamo_client = DynamoClient()

router = APIRouter(
    prefix="/committee",
    tags=["committee"],
    responses={404: {"description": "Not found"}}
)


@router.get("/")
async def get_members():
    table = dynamo_client.Table('committee')
    response = table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    return data


# @router.get("/{id}")
# async def get_member(id: str):
#     return json.loads(dumps(db_client.db.committee.find({"_id": ObjectId(id)})))


# @router.post("/")
# async def add_member(name: str = Form(...), role: str = Form(...), profile_pic: UploadFile = File(...)):
#     member = {
#         "picture_bin": profile_pic.file.read(),
#         "name": name,
#         "role": role
#     }
#     new_member = db_client.db.committee.insert_one(member).inserted_id
#     return json.loads(dumps(new_member))
