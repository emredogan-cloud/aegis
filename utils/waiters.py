from clients.ec2_client import get_ec2_client
from clients.dynamodb_client import get_dynamodb_client
from clients.kms_client import get_kms_client
from utils.logger import get_logger

logger = get_logger("waiters")


def wait_for_ec2_running(instance_id):
    ec2 = get_ec2_client()
    logger.info(f"EC2 | Waiting for instance to be running | {instance_id}")

    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])

    logger.info(f"EC2 | Instance is running | {instance_id}")


def wait_for_ec2_terminated(instance_ids):
    ec2 = get_ec2_client()
    logger.info(f"EC2 | Waiting for instances termination | {instance_ids}")

    waiter = ec2.get_waiter("instance_terminated")
    waiter.wait(InstanceIds=instance_ids)

    logger.info("EC2 | Instances terminated")


def wait_for_dynamodb_active(table_name):
    dynamodb = get_dynamodb_client()
    logger.info(f"DynamoDB | Waiting for table to become ACTIVE | {table_name}")

    waiter = dynamodb.get_waiter("table_exists")
    waiter.wait(TableName=table_name)

    logger.info(f"DynamoDB | Table is ACTIVE | {table_name}")


def wait_for_kms_enabled(key_id):
    kms = get_kms_client()
    logger.info(f"KMS | Waiting for key to be enabled | {key_id}")

    while True:
        meta = kms.describe_key(KeyId=key_id)["KeyMetadata"]
        if meta["KeyState"] == "Enabled":
            break

    logger.info(f"KMS | Key is enabled | {key_id}")
