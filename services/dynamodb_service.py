from utils.logger import get_logger
from clients.dynamodb_client import get_dynamodb_client
from botocore.exceptions import ClientError
from config import DYNAMODB_BILLING_MODE
from utils.waiters import wait_for_dynamodb_active

logger = get_logger("dynamodb_service")

def create_audit_table(table_name):
    dynamodb = get_dynamodb_client()

    try:
        logger.info(f"DynamoDB Table Creating | {table_name}")

        dynamodb.create_table(
            TableName=table_name,
            DeletionProtectionEnabled=True,

            AttributeDefinitions=[
                {
                    "AttributeName": "file_id",
                    "AttributeType": "S"
                }
            ],

            KeySchema=[
                {
                    "AttributeName": "file_id",
                    "KeyType": "HASH"
                }
            ],

            BillingMode= DYNAMODB_BILLING_MODE ,
            
            Tags=[
                {
                    "Key": "environment",
                    "Value": "test"
                }
            ],
        )

        wait_for_dynamodb_active(table_name)

        logger.info(f"DynamoDB Table ACTIVE | {table_name}")
        return True

    except ClientError as e:
        if e.response["Error"]["Code"] == 'ResourceInUseException':
            logger.warning(f"DynamoDB table already exists | {table_name}")
            return True
        else:
            logger.error(f'ERROR : {e}')
            return False
        

def delete_dynamodb_table(table_name):
    dynamodb = get_dynamodb_client()

    try:
        dynamodb.delete_table(TableName=table_name)
        logger.info(f"DynamoDB table deleted: {table_name}")
    except ClientError:
        pass

