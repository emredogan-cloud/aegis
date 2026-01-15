from utils.logger import get_logger
from config import *

from services.ec2_service import delete_ec2_resources
from services.iam_service import delete_iam_resources
from services.dynamodb_service import delete_dynamodb_table
from services.s3_service import delete_bucket
from services.kms_service import delete_kms_key_by_alias

logger = get_logger("cleanup")

def cleanup():
    logger.info("🔥 Aegis Infrastructure Cleanup Started")

    delete_ec2_resources(
        EC2_KEY_PAIR_NAME,
        EC2_SECURITY_GROUP_NAME
    )

    delete_iam_resources(
        IAM_ROLE_NAME,
        IAM_INSTANCE_PROFILE_NAME,
        "AegisInlinePolicy"
    )

    delete_dynamodb_table(DYNAMODB_TABLE_NAME)

    delete_bucket(S3_BUCKET_NAME)

    delete_kms_key_by_alias(KMS_ALIAS_NAME)

    logger.info("✅ All resources cleaned successfully")


if __name__ == "__main__":
    cleanup()
