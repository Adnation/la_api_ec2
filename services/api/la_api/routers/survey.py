from datetime import datetime
from fastapi import APIRouter

from la_api.dynamo_utils import DynamoClient

dynamo_client = DynamoClient()

router = APIRouter(
    prefix="/survey",
    tags=["survey"],
    responses={404: {"description": "Not found"}}
)


@router.get("/fetch-all")
async def get_surveys():
    table = dynamo_client.Table('surveys')
    response = table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    dated_survey = []
    tbd_survey = []
    for d in data:
        if 'date' not in d or d['date'].upper() == 'TBD':
            tbd_survey.append(d)

        if datetime.strptime(d['date'], '%m-%d-%Y').date() >= datetime.now().date():
            d['date'] = datetime.strptime(d['date'], '%m-%d-%Y').date()
            dated_survey.append(d)

    dated_survey.sort(key=lambda item: item['date'], reverse=True)
    dated_survey.extend(tbd_survey)
    return dated_survey
