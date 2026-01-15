import boto3
from config import AWS_REGION

def get_iam_client():
    return boto3.client('iam',region_name=AWS_REGION)