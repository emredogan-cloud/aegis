from botocore.exceptions import ClientError
from utils.logger import get_logger
from clients.kms_client import get_kms_client
from config import KMS_ALIAS_NAME
from utils.waiters import wait_for_kms_enabled

logger = get_logger("kms_service")


def get_key_by_alias(alias_name: str):
    kms = get_kms_client()

    try:
        response = kms.describe_key(KeyId=alias_name)
        meta = response["KeyMetadata"]

        logger.info(f"KMS | Key found by alias | {alias_name}")
        return meta["KeyId"], meta["Arn"]

    except ClientError as e:
        if e.response["Error"]["Code"] == "NotFoundException":
            logger.info(f"KMS | Alias not found | {alias_name}")
            return None, None

        logger.error(f"KMS | DescribeKey failed | {e}")
        raise


def create_master_key_with_alias(alias_name: str):
    kms = get_kms_client()

    logger.info("KMS | Creating new master key")

    response = kms.create_key(
        Description="Aegis Master Symmetric Key",
        KeyUsage="ENCRYPT_DECRYPT",
        Origin="AWS_KMS"
    )

    meta = response["KeyMetadata"]
    key_id = meta["KeyId"]
    key_arn = meta["Arn"]

    wait_for_kms_enabled(key_id)

    kms.create_alias(
        AliasName=alias_name,
        TargetKeyId=key_id
    )

    logger.info(f"KMS | Key created and alias assigned | {alias_name}")

    return key_id, key_arn


def create_master_key():
    """
    Alias varsa mevcut key kullanılır.
    Yoksa yeni key oluşturulur.
    """

    key_id, key_arn = get_key_by_alias(KMS_ALIAS_NAME)

    if key_id:
        return key_id, key_arn

    return create_master_key_with_alias(KMS_ALIAS_NAME)


def delete_kms_key_by_alias(alias_name):
    kms = get_kms_client()

    try:
        meta = kms.describe_key(KeyId=alias_name)["KeyMetadata"]
        key_id = meta["KeyId"]

        kms.delete_alias(AliasName=alias_name)

        kms.schedule_key_deletion(
            KeyId=key_id,
            PendingWindowInDays=7
        )

        logger.info(f"KMS | Key scheduled for deletion | {key_id}")

    except ClientError as e:
        logger.warning(f"KMS | Cleanup skipped | {e.response['Error']['Code']}")
