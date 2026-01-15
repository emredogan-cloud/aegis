import boto3
from config import AWS_REGION

def get_s3_client():
    return boto3.client('s3', region_name=AWS_REGION)