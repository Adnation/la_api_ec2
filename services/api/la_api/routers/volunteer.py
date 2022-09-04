import os
import re
import json
import boto3
import calendar
from datetime import datetime

from fastapi import UploadFile
from bson.json_util import dumps
from bson.objectid import ObjectId
from botocore.exceptions import ClientError
from fastapi import APIRouter, Form, File, Request, HTTPException

from la_api.dynamo_utils import DynamoClient

dynamo_client = DynamoClient()

router = APIRouter(
    prefix="/volunteer",
    tags=["volunteer"],
    responses={404: {"description": "Not found"}}
)


@router.post("/post-request")
async def post_request(request: Request):
    payload = await request.json()
    for f in ['name', 'email', 'phone']:
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
        'name': {
            'S': payload['name']
        },
        'email': {
            'S': payload['email']
        },
        'phone': {
            'S': payload['phone']
        },
        'free_message': {
            'S': payload.get('free_message', '')
        }
    }

    client.put_item(TableName='volunteer', Item=item)
    return {'status': 'success'}
