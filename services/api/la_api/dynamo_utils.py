import os
import boto3


class DynamoClient:

    def __new__(cls):
        if not hasattr(cls, 'instance'):

            if os.getenv("ENVIRONMENT") == 'dev':
                cls.instance = boto3.resource(
                    'dynamodb',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION")
                )
            else:
                cls.instance = boto3.resource(
                    'dynamodb',
                    region_name=os.getenv("AWS_REGION")
                )
        return cls.instance
