import boto3
from config import AWS_REGION

def get_dynamodb_client():
    return boto3.client('dynamodb', region_name=AWS_REGION)