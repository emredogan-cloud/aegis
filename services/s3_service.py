from botocore.exceptions import ClientError
from utils.logger import get_logger
from config import AWS_REGION
from clients.s3_client import get_s3_client

logger = get_logger("s3_service")

def create_bucket(bucket_name):
    s3 = get_s3_client()

    try:
        if AWS_REGION == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": AWS_REGION
                }
            )

        logger.info(f"S3 Bucket Created successfully| {bucket_name}")
        return True

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        logger.error(f"S3 CreateBucket operation Failed | {error_code} | {error_message}")
        return False


def delete_bucket(bucket_name):
    s3 = get_s3_client()

    try:
        objs = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in objs:
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects":[{"Key":o["Key"]} for o in objs["Contents"]]}
            )

        s3.delete_bucket(Bucket=bucket_name)
        logger.info(f"S3 bucket deleted: {bucket_name}")
    except ClientError:
        pass
