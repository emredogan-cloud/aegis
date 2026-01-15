import time
import json
from botocore.exceptions import ClientError
from utils.logger import get_logger
from clients.iam_client import get_iam_client
from data.policies import EC2_TRUST_POLICY, build_permission_policy

logger = get_logger("iam_service")


def create_role(role_name: str) -> bool:
    iam = get_iam_client()

    try:
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(EC2_TRUST_POLICY)
        )

        logger.info(f"IAM Role Created | {role_name}")
        time.sleep(2)
        return True

    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            logger.warning(f"IAM Role Already Exists | {role_name}")
            return True

        logger.error(f"IAM CreateRole Failed | {e}")
        return False


def put_inline_policy(role_name: str, policy_name: str, policy_doc: dict) -> bool:
    iam = get_iam_client()

    try:
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_doc)
        )

        logger.info(f"Inline Policy Attached | {policy_name}")
        return True

    except ClientError as e:
        logger.error(f"PutRolePolicy Creation Failed | {e}")
        return False


def ensure_instance_profile(profile_name: str) -> bool:
    iam = get_iam_client()

    try:
        iam.create_instance_profile(InstanceProfileName=profile_name)
        logger.info(f"Instance Profile Created | {profile_name}")
        return True

    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            logger.warning(f"Instance Profile Already Exists | {profile_name}")
            return True

        logger.error(f"CreateInstanceProfile Operation Failed | {e}")
        return False


def add_role_to_profile(profile_name: str, role_name: str) -> bool:
    iam = get_iam_client()

    try:
        iam.add_role_to_instance_profile(
            InstanceProfileName=profile_name,
            RoleName=role_name
        )

        logger.info(f"Role Added To Profile | {role_name} -> {profile_name}")
        return True

    except ClientError as e:
        if e.response["Error"]["Code"] in ["LimitExceeded", "EntityAlreadyExists"]:
            logger.warning("Role already attached to profile")
            return True

        logger.error(f"AddRoleToProfile Failed | {e}")
        return False


def setup_iam_infrastructure(
    role_name,
    profile_name,
    policy_name,
    bucket_arn,
    table_arn,
    kms_key_arn
) -> bool:

    if not create_role(role_name):
        return False

    policy_doc = build_permission_policy(bucket_arn, table_arn, kms_key_arn)

    if not put_inline_policy(role_name, policy_name, policy_doc):
        return False

    if not ensure_instance_profile(profile_name):
        return False

    if not add_role_to_profile(profile_name, role_name):
        return False

    logger.info("IAM Infrastructure Setup Completed Successfully")
    return True


def delete_iam_resources(role_name, profile_name, policy_name):
    iam = get_iam_client()

    try:
        iam.remove_role_from_instance_profile(
            InstanceProfileName=profile_name,
            RoleName=role_name
        )
    except ClientError:
        pass

    try:
        iam.delete_instance_profile(InstanceProfileName=profile_name)
    except ClientError:
        pass

    try:
        iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
    except ClientError:
        pass

    try:
        iam.delete_role(RoleName=role_name)
    except ClientError:
        pass

    logger.info("IAM resources deleted")
