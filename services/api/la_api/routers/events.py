import os
import boto3

from datetime import datetime
from fastapi import APIRouter

from la_api.configs import S3_BUCKET_NAME, S3_EVENT_PHOTOS_PREFIX
from la_api.dynamo_utils import DynamoClient

dynamo_client = DynamoClient()

router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Not found"}}
)


@router.get("/upcoming-events")
async def get_events():
    table = dynamo_client.Table('events')
    response = table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    dated_events = []
    tbd_events = []
    for d in data:
        if d['date'] == 'TBD':
            tbd_events.append(d)
            continue

        if datetime.strptime(d['date'], '%m-%d-%Y').date() >= datetime.now().date():
            d['date'] = datetime.strptime(d['date'], '%m-%d-%Y').date()
            dated_events.append(d)

    dated_events.sort(key=lambda item: item['date'], reverse=True)
    dated_events.extend(tbd_events)
    return dated_events


@router.get("/past-events")
async def get_events():
    table = dynamo_client.Table('events')
    response = table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    past_events = []
    for d in data:
        if d['date'] == 'TBD':
            continue
        if datetime.strptime(d['date'], '%m-%d-%Y').date() < datetime.now().date():
            past_events.append(d)

    return past_events


@router.get("/get-latest-photos")
async def get_latest_photos():
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(S3_BUCKET_NAME)
    files = my_bucket.objects.filter(Prefix=S3_EVENT_PHOTOS_PREFIX)
    # files = [f"https:///s3-{os.getenv('AWS_REGION')}.amazonaws.com/{S3_BUCKET_NAME}/{obj.key}" for obj in sorted(
    #     files, key=lambda x: x.last_modified, reverse=True)][0:10]

    t_files = []
    for obj in sorted(files, key=lambda x: x.last_modified, reverse=True):
        t_files.append({
            "src": f"https:///s3-{os.getenv('AWS_REGION')}.amazonaws.com/{S3_BUCKET_NAME}/{obj.key}"
        })

    return t_files[0:10]


@router.get("/get-event-photos/{id}")
async def get_latest_photos(id: str):
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(S3_BUCKET_NAME)
    files = my_bucket.objects.filter(Prefix=f"{S3_EVENT_PHOTOS_PREFIX}/{id}")
    t_files = []
    for obj in sorted(files, key=lambda x: x.last_modified, reverse=True):
        t_files.append({
            "src": f"https:///s3-{os.getenv('AWS_REGION')}.amazonaws.com/{S3_BUCKET_NAME}/{obj.key}",
            "width": 6,
            "height": 4
        })

    # files = [f"https:///s3-{os.getenv('AWS_REGION')}.amazonaws.com/{S3_BUCKET_NAME}/{obj.key}" for obj in sorted(
    #     files, key=lambda x: x.last_modified, reverse=True)]
    return t_files
