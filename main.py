from utils.logger import get_logger
from config import *
from services.kms_service import create_master_key
from services.s3_service import create_bucket
from services.dynamodb_service import create_audit_table
from services.iam_service import setup_iam_infrastructure
from services.ec2_service import provision_ec2_instance

logger = get_logger("main")

def main():
    logger.info("Aegis Infrastructure Provisioning Started")

    # 1. KMS
    logger.info("Step 1: Creating KMS Master Key")
    key_id, key_arn = create_master_key()
    if not key_arn:
        raise Exception("KMS Key creation failed")
    logger.info(f"KMS Key Ready | KeyId={key_id}")

    # 2. S3
    logger.info("Step 2: Creating S3 Bucket")
    if not create_bucket(S3_BUCKET_NAME):
        raise Exception("S3 bucket creation failed")
    bucket_arn = f"arn:aws:s3:::{S3_BUCKET_NAME}"
    logger.info(f"S3 Bucket Ready | {bucket_arn}")

    # 3. DynamoDB
    logger.info("Step 3: Creating DynamoDB Table")
    if not create_audit_table(DYNAMODB_TABLE_NAME):
        raise Exception("DynamoDB table creation failed")
    table_arn = f"arn:aws:dynamodb:{AWS_REGION}:{AWS_ACCOUNT_ID}:table/{DYNAMODB_TABLE_NAME}"
    logger.info(f"DynamoDB Table Ready | {table_arn}")

    # 4. IAM
    logger.info("Step 4: Setting up IAM Infrastructure")
    if not setup_iam_infrastructure(
        IAM_ROLE_NAME,
        IAM_INSTANCE_PROFILE_NAME,
        "AegisInlinePolicy",
        bucket_arn,
        table_arn,
        key_arn
    ):
        raise Exception("IAM setup failed")
    logger.info("IAM Infrastructure Ready")

    # 5. EC2
    logger.info("Step 5: Provisioning EC2 Instance")
    public_ip = provision_ec2_instance(
        EC2_KEY_PAIR_NAME,
        EC2_SECURITY_GROUP_NAME,
        SSH_ALLOWED_CIDR,
        IAM_INSTANCE_PROFILE_NAME
    )

    logger.info(f"EC2 Instance Ready | Public IP = {public_ip}")

    logger.info("Aegis Infrastructure Provisioning Completed")

if __name__ == "__main__":
    main()

