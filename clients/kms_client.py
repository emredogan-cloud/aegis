import boto3
from config import AWS_REGION

def get_kms_client():
    return boto3.client('kms', region_name=AWS_REGION)