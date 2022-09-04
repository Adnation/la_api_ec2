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

router = APIRouter(
    prefix="/rsvp",
    tags=["rsvp"],
    responses={404: {"description": "Not found"}}
)


@router.get("/")
async def get_events():
    table = dynamo_client.Table('rsvp')
    response = table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    return data


@router.post("/post")
async def add_rsvp(request: Request):
    payload = await request.json()
    for f in ['event_id', 'name', 'email', 'phone', 'free_text', 'members']:
        if f not in payload:
            raise HTTPException(status_code=400, detail=f"Missing {f} in payload")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", payload['email']):
        raise HTTPException(status_code=400, detail=f"Invalid email address")

    client = boto3.client(
        "dynamodb",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"))

    item = {
        'id': {
            'S': f"{payload['event_id']}___{payload['email']}"
        },
        'event_id': {
            'S': payload['event_id']
        },
        'name': {
            'S': payload['name']
        },
        'email': {
            'S': payload['email']
        },
        'phone': {
            'S': payload['phone']
        },
        'free_text': {
            'S': payload['free_text']
        },
        'members': {
            'N': str(payload['members'])
        }
    }

    client.put_item(TableName='rsvp', Item=item)
    return {'status': 'success'}


