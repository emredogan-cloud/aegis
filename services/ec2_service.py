from botocore.exceptions import ClientError
from clients.ec2_client import get_ec2_client
from clients.ssm_client import get_ssm_client
from utils.logger import get_logger
import os
from utils.waiters import wait_for_ec2_running , wait_for_ec2_terminated
logger = get_logger("ec2_service")

INSTANCE_TAG_NAME = "Aegis-Worker"


def find_existing_instance():
    ec2 = get_ec2_client()

    response = ec2.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [INSTANCE_TAG_NAME]},
            {"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]}
        ]
    )

    for res in response["Reservations"]:
        for ins in res["Instances"]:
            return ins

    return None


def create_key_pair(key_name: str) -> str:
    ec2 = get_ec2_client()

    try:
        response = ec2.create_key_pair(KeyName=key_name)

        with open(f"{key_name}.pem", "w") as f:
            f.write(response["KeyMaterial"])

        os.chmod(f"{key_name}.pem", 0o400)

        logger.info(f"KeyPair created: {key_name}")
        return key_name

    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidKeyPair.Duplicate":
            logger.warning(f"KeyPair already exists: {key_name}")
            return key_name
        raise


def get_latest_ami() -> str:
    ssm = get_ssm_client()
    return ssm.get_parameter(
        Name="/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64",
        WithDecryption=False
    )["Parameter"]["Value"]


def launch_instance(ami_id, key_name, sg_id, profile_name) -> str:
    ec2 = get_ec2_client()

    existing = find_existing_instance()

    if existing:
        instance_id = existing["InstanceId"]
        state = existing["State"]["Name"]

        logger.info(f"Existing instance found | {instance_id} | state={state}")

        if state == "stopped":
            ec2.start_instances(InstanceIds=[instance_id])
            waiter = ec2.get_waiter("instance_running")
            waiter.wait(InstanceIds=[instance_id])

        desc = ec2.describe_instances(InstanceIds=[instance_id])
        public_ip = desc["Reservations"][0]["Instances"][0].get("PublicIpAddress")

        logger.info(f"Reused EC2 instance | Public IP = {public_ip}")
        return public_ip

    user_data_script = """#!/bin/bash
dnf update -y
dnf install python3-pip -y
pip3 install boto3
echo "Aegis Setup Complete" > /home/ec2-user/setup_log.txt
"""

    logger.info("Creating new EC2 instance...")

    response = ec2.run_instances(
        ImageId=ami_id,
        InstanceType="t2.micro",
        KeyName=key_name,
        SecurityGroupIds=[sg_id],
        MinCount=1,
        MaxCount=1,
        UserData=user_data_script,
        IamInstanceProfile={"Name": profile_name},
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": INSTANCE_TAG_NAME}
                ]
            }
        ]
    )

    instance_id = response["Instances"][0]["InstanceId"]

    wait_for_ec2_running(instance_id)

    desc = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = desc["Reservations"][0]["Instances"][0].get("PublicIpAddress")

    logger.info(f"New EC2 instance ready | {instance_id} | Public IP = {public_ip}")
    return public_ip



def delete_ec2_resources(key_name, group_name):
    ec2 = get_ec2_client()

    instances = ec2.describe_instances(
        Filters=[{"Name": "tag:Name", "Values": [INSTANCE_TAG_NAME]}]
    )

    ids = []
    for r in instances["Reservations"]:
        for i in r["Instances"]:
            ids.append(i["InstanceId"])

    if ids:
        logger.info(f"Terminating instances: {ids}")
        ec2.terminate_instances(InstanceIds=ids)
        wait_for_ec2_terminated(instance_ids=ids)

    try:
        groups = ec2.describe_security_groups(Filters=[{"Name":"group-name","Values":[group_name]}])
        for g in groups["SecurityGroups"]:
            ec2.delete_security_group(GroupId=g["GroupId"])
            logger.info(f"Deleted SG: {group_name}")
    except ClientError:
        pass

    try:
        ec2.delete_key_pair(KeyName=key_name)
        logger.info(f"Deleted KeyPair: {key_name}")
    except ClientError:
        pass
