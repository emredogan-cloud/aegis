import boto3
from config import AWS_REGION

def get_ec2_client():
    return boto3.client('ec2',region_name=AWS_REGION)