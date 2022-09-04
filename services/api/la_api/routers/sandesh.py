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
    prefix="/sandesh",
    tags=["sandesh"],
    responses={404: {"description": "Not found"}}
)


@router.get("/get-archive")
async def get_archive():

    if os.getenv("ENVIRONMENT") == 'dev':
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    else:
        session = boto3.Session()
    s3 = session.resource('s3')
    my_bucket = s3.Bucket('la-dfw')

    tmp_dict = {}
    last_three = [str(datetime.now().year - i) for i in [0, 1, 2]]

    for y in last_three:
        tmp_dict[str(y)] = []

    current_name = f"{datetime.now().strftime('%B')}-{datetime.now().year}"
    print(current_name)
    for objects in my_bucket.objects.filter(Prefix="sandesh/"):
        if '.pdf' not in objects.key:
            continue
        name = objects.key.replace('sandesh/', '').replace('.pdf', '').title()
        href = f'https://la-dfw.s3.amazonaws.com/{objects.key}'

        month, year = name.split('-')
        month = month.title()
        tmp_dict[year].append({
            'name': month.title(),
            'href': href
        })

    months = list(calendar.month_name)
    archive = []
    current = {}
    for index, year in enumerate(last_three):
        if index == 0:
            if len(tmp_dict[year]):
                sorted_list = sorted(tmp_dict[year], key=lambda t: months.index(t['name']))
                current = sorted_list[-1]
                sorted_list = sorted_list[0: len(sorted_list) - 1]
                archive.append({
                    'year': year,
                    'archive': sorted_list
                })
        else:
            archive.append({
                'year': year,
                'archive': sorted(tmp_dict[year], key=lambda t: months.index(t['name']))
            })

    return {
        'current': current,
        'archive': archive
    }


@router.post("/post-request")
async def post_request(request: Request):
    payload = await request.json()
    for f in ['name', 'email', 'subject', 'message']:
        if f not in payload:
            raise HTTPException(status_code=400, detail=f"Missing {f} in payload")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", payload['email']):
        raise HTTPException(status_code=400, detail=f"Invalid email address")

    sender = "adityathakkar29@gmail.com"
    recipient = "adityathakkar29@gmail.com"
    aws_region = "us-east-2"
    subject = f"EMAIL REQUEST FOR LOHANA SANDESH: {payload['subject']}"
    body_html = f"""
    <html>
        <body>
            <p>NAME: {payload['name']}</p>
            <hr></hr>
            <p>FROM: {payload['email']}</p>
            <hr></hr>
            <p>SUBJECT: {payload['subject']}</p>
            <hr></hr>
            <p>MESSAGE: {payload['message']}</p>
            <hr></hr>
        </body>
    </html>
    """
    charset = "UTF-8"
    if os.getenv("ENVIRONMENT") == 'dev':
        client = boto3.client(
            'ses',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=aws_region
        )
    else:
        client = boto3.client('ses', region_name=aws_region)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': ["thakkarmayur@hotmail.com",],
                'CcAddresses': [
                    'adityathakkar29@gmail.com',
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    }
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    return {
        'status': True
    }
