import boto3
from config import AWS_REGION

def get_ssm_client():
    return boto3.client('ssm', region_name=AWS_REGION)