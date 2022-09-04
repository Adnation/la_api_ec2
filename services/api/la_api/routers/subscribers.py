import os
import re
import json
import boto3

from fastapi import UploadFile
from bson.json_util import dumps
from bson.objectid import ObjectId
from fastapi import APIRouter, Form, File, Request, HTTPException

from la_api.dynamo_utils import DynamoClient

dynamo_client = DynamoClient()

table_name = prefix = 'subscribers'

router = APIRouter(
    prefix=f"/{prefix}",
    tags=[prefix],
    responses={404: {"description": "Not found"}}
)


fields = ['name', 'email', 'phone']


@router.get("/")
async def get_subs():
    global table_name
    table = dynamo_client.Table(table_name)
    response = table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    return data


@router.get("/{id}")
async def get_sub(id: str):
    return []


@router.post("/post")
async def add_sub(request: Request):
    global fields
    payload = await request.json()
    item = {
        'name': {
            'S': ''
        },
        'email': {
            'S': ''
        },
        'phone': {
            'S': ''
        }
    }
    for f in fields:
        if f not in payload:
            raise HTTPException(status_code=400, detail=f"Missing {f} in payload")
        else:
            item[f]['S'] = payload[f]

    if not re.match(r"[^@]+@[^@]+\.[^@]+", payload['email']):
        raise HTTPException(status_code=400, detail=f"Invalid email address")

    client = boto3.client(
        "dynamodb",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"))

    client.put_item(TableName=table_name, Item=item)
    return {'status': 'success'}
