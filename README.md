# Aegis AWS Infrastructure Automation Tool

![CI Status](https://github.com/emredogan-cloud/aegis/actions/workflows/ci.yml/badge.svg)

Aegis is a production-grade AWS infrastructure automation tool written in Python using Boto3.  
It provisions and destroys AWS resources in an idempotent, secure, and modular way.

This project is designed as a Terraform-like automation pipeline using pure Python.

---

## 🚀 Features

- Idempotent provisioning and cleanup
- Modular service architecture
- Least-privilege IAM policy generation
- KMS alias-based key lifecycle management
- EC2 instance reuse via tag-based discovery
- Centralized waiter abstraction layer
- Full infrastructure lifecycle management
- Production-grade logging
- Terraform-like apply / destroy behavior

---

## 🧱 Architecture

main.py -> Provision orchestrator
cleanup.py -> Destroy orchestrator

services/ -> AWS service lifecycle logic
clients/ -> Boto3 client factories
utils/ -> Logger and waiters
data/ -> IAM policy builders
config.py -> Central configuration


---

## 🔁 Provision Flow

`python main.py` performs:

1. Create or reuse KMS master key (alias controlled)
2. Create S3 bucket
3. Create DynamoDB audit table
4. Create IAM role, policy, and instance profile
5. Provision EC2 instance (tag-based idempotent)
6. Return public IP of the worker instance

---

## 🧹 Cleanup Flow

`python cleanup.py` performs:

1. Terminate EC2 instances
2. Delete security group
3. Delete key pair
4. Remove IAM profile, policy and role
5. Delete DynamoDB table
6. Empty and delete S3 bucket
7. Remove KMS alias and schedule key deletion

This mirrors Terraform destroy behavior.

---

## 🔐 Security Design

- KMS symmetric encryption with alias lifecycle
- IAM least-privilege policy builder
- Instance profile based permissions
- No hard-coded credentials
- SSH restricted by CIDR
- Audit-ready DynamoDB table

---

## ⚙️ Configuration

All configuration is managed in `config.py`:

```python
AWS_REGION
AWS_ACCOUNT_ID

S3_BUCKET_NAME
DYNAMODB_TABLE_NAME

IAM_ROLE_NAME
IAM_INSTANCE_PROFILE_NAME

EC2_KEY_PAIR_NAME
EC2_SECURITY_GROUP_NAME
SSH_ALLOWED_CIDR

KMS_ALIAS_NAME
DYNAMODB_BILLING_MODE


▶️ Usage

Provision infrastructure
  python main.py


Destroy infrastructure
  python cleanup.py

📦 Requirements
  pip install boto3


AWS credentials must be configured via:
  aws configure



🧠 Design Principles

Idempotency first

Separation of concerns

Explicit orchestration

Infrastructure lifecycle ownership

Cloud-native security design

Production-ready logging


## 📦 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt

## Installatıon 

### 1. Clone the repository

```bash
git clone https://github.com/emredogan-cloud/aegis.git
cd aegis


Set up a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

📜 License

MIT License
