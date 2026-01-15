from utils.logger import get_logger

logger = get_logger("policies")

EC2_TRUST_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    ]
}


def build_permission_policy(bucket_arn: str, table_arn: str, kms_key_arn: str) -> dict:
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowPutObjectToVaultBucket",
                "Effect": "Allow",
                "Action": "s3:PutObject",
                "Resource": f"{bucket_arn}/*"
            },
            {
                "Sid": "AllowPutItemToMetadataTable",
                "Effect": "Allow",
                "Action": "dynamodb:PutItem",
                "Resource": table_arn
            },
            {
                "Sid": "AllowGenerateDataKeyWithVaultKmsKey",
                "Effect": "Allow",
                "Action": "kms:GenerateDataKey",
                "Resource": kms_key_arn
            }
        ]
    }

    logger.info(
        f"Permission policy built | "
        f"S3={bucket_arn} | DynamoDB={table_arn} | KMS={kms_key_arn}"
    )

    return policy
