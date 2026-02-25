# Aegis Docker Documentation

## Overview

Aegis can be containerized and run in Docker for consistent, isolated AWS infrastructure provisioning. This guide covers building, running, and managing Aegis in containers.

---

## Building the Image

### Standard Build

```bash
docker build -t aegis:latest .
```

### With Build Args (optional)

```bash
docker build -t aegis:v1.0 --build-arg PYTHON_VERSION=3.11 .
```

---

## Running Aegis

### Option 1: With AWS Credentials from Environment Variables

```bash
docker run \
  --env AWS_REGION=us-east-1 \
  --env AWS_ACCESS_KEY_ID=<your-key> \
  --env AWS_SECRET_ACCESS_KEY=<your-secret> \
  aegis:latest
```

### Option 2: With AWS Credentials from Host

```bash
docker run \
  -v ~/.aws:/home/aegis/.aws:ro \
  aegis:latest
```

### Option 3: Using Docker Compose (Recommended)

```bash
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
docker-compose up
```

---

## Cleanup

### Remove EC2 Resources

Run cleanup.py instead of main.py:

```bash
docker run \
  -v ~/.aws:/home/aegis/.aws:ro \
  aegis:latest \
  python cleanup.py
```

### Stop and Remove Container

```bash
docker-compose down
```

### Remove Image

```bash
docker rmi aegis:latest
```

---

## Security Best Practices

1. **Don't commit credentials** to version control
2. **Use IAM roles** in production (mount from EC2 metadata)
3. **Read-only AWS volume** (`-v ~/.aws:/home/aegis/.aws:ro`)
4. **Non-root user** (aegis:1000) for container security
5. **Resource limits** (CPU/memory) in docker-compose

---

## Troubleshooting

### Check logs

```bash
docker logs -f <container-id>
```

### Interactive shell

```bash
docker run -it -v ~/.aws:/home/aegis/.aws:ro aegis:latest /bin/bash
```

### Verify AWS connectivity

```bash
docker run -it aegis:latest python -c "import boto3; print(boto3.__version__)"
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Build and push Aegis
  uses: docker/build-push-action@v5
  with:
    context: ./
    push: true
    tags: ${{ secrets.REGISTRY }}/aegis:latest
```

### GitLab CI Example

```yaml
build:
  image: docker:latest
  script:
    - docker build -t aegis:latest .
    - docker login -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN $CI_REGISTRY
    - docker push aegis:latest
```

---

## Advanced Usage

### Run Both Provision and Cleanup

```bash
# Provision
docker run -v ~/.aws:/home/aegis/.aws:ro aegis:latest

# Later, cleanup
docker run -v ~/.aws:/home/aegis/.aws:ro aegis:latest python cleanup.py
```

### Mount config.py for custom settings

```bash
docker run \
  -v ~/.aws:/home/aegis/.aws:ro \
  -v $(pwd)/config.py:/app/config.py:ro \
  aegis:latest
```

### Persistent logs

```bash
docker run \
  -v ~/.aws:/home/aegis/.aws:ro \
  -v $(pwd)/logs:/app/logs \
  aegis:latest
```

---

## Docker Registry (Optional)

### Push to AWS ECR

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag aegis:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/aegis:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/aegis:latest
```

### Pull from ECR

```bash
docker pull <account-id>.dkr.ecr.us-east-1.amazonaws.com/aegis:latest
```

---

## Summary

| Method | Command |
|--------|---------|
| **Build** | `docker build -t aegis:latest .` |
| **Run (env vars)** | `docker run -e AWS_REGION=... aegis:latest` |
| **Run (AWS volume)** | `docker run -v ~/.aws:... aegis:latest` |
| **Run (compose)** | `docker-compose up` |
| **Cleanup** | `docker run ... python cleanup.py` |
| **Logs** | `docker logs -f <container-id>` |

---

See `docker-compose.yml` for production-ready configuration.
