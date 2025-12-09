# YANTECH Notification System - Backend Services

## Overview

Microservices backend for the YANTECH Notification System, providing secure APIs for application management, authentication, and multi-channel notification delivery (Email, SMS, Push).

## 🏗️ Architecture

### Services

**Admin Service** (`admin/`)
- Application and API key management
- User authentication
- AWS resource provisioning (SES, SNS)
- Port: 8080

**Requestor Service** (`requestor/`)
- Notification request processing
- JWT authentication
- SQS message queuing
- Port: 80

**Worker Service** (`worker/`)
- Notification delivery (Email, SMS, Push)
- SQS message processing
- Delivery status tracking
- Background processing

### Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: AWS DynamoDB
- **Queue**: AWS SQS
- **Notifications**: AWS SES (Email), SNS (SMS/Push)
- **Authentication**: JWT tokens with API keys
- **Deployment**: Docker + AWS ECS

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- AWS CLI configured
- AWS Account with appropriate permissions

### Local Development

**1. Clone Repository**
```bash
git clone https://github.com/YANTECH-NP/YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin.git
cd YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin
```

**2. Set Up Environment**
```bash
# Admin service
cd admin
cp .env.example .env
# Edit .env with your AWS credentials and configuration

# Requestor service
cd ../requestor
cp .env.example .env

# Worker service
cd ../worker
cp .env.example .env
```

**3. Run with Docker Compose**
```bash
docker-compose up --build
```

**4. Access Services**
- Admin API: http://localhost:8080
- Requestor API: http://localhost:80
- API Documentation: http://localhost:8080/docs

### Running Individual Services

**Admin Service:**
```bash
cd admin
pip install -r requirements.txt
uvicorn server:app --reload --port 8080
```

**Requestor Service:**
```bash
cd requestor
pip install -r requirements.txt
uvicorn app.main:app --reload --port 80
```

**Worker Service:**
```bash
cd worker
python -m app.main
```

## 📚 Service Documentation

### Admin Service

See [admin/README.md](./admin/README.md) for:
- API endpoints
- Authentication flow
- Application management
- API key generation

### Worker Service

See [worker/README.md](./worker/README.md) for:
- SQS message processing
- Notification delivery
- Error handling
- Retry logic

## 🔐 Authentication

### API Key Authentication

1. **Register Application** (Admin API)
```bash
POST /app
{
  "Application": "MY_APP",
  "App_name": "My Application",
  "Description": "Application description"
}
```

2. **Get JWT Token** (Requestor API)
```bash
POST /auth
Headers: x-api-key: your-api-key
Body: {"application_id": "MY_APP"}
```

3. **Use Token for Requests**
```bash
POST /notifications
Headers: Authorization: Bearer jwt-token
Body: {notification data}
```

## 🧪 Testing

### Run All Tests
```bash
# Windows
run-tests.bat

# Linux/Mac
./run-tests.sh
```

### Run Specific Tests
```bash
# Admin service tests
pytest tests/admin/ -v

# Requestor service tests
pytest tests/requestor/ -v

# Worker service tests
pytest tests/worker/ -v

# Integration tests
pytest tests/integration/ -v
```

### Test Coverage
```bash
pytest --cov=. --cov-report=html
# View coverage report in htmlcov/index.html
```

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for detailed testing documentation.

## 🚀 Deployment

### Automated Deployment (GitHub Actions)

**Branch Deployments:**
- `dev` branch → dev environment (auto-tagged: `{sha}-dev-{timestamp}`)
- `staging` branch → staging environment (auto-tagged: `{sha}-staging-{timestamp}`)

**Production Releases (Tags):**
```bash
# Create release using script
./scripts/create-release.sh 1.0.0 "Initial production release"

# Or manually
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

See [RELEASE_GUIDE.md](./docs/RELEASE_GUIDE.md) for detailed instructions.

### Manual Deployment

```bash
# Build and push Docker image
docker build -t admin-service:latest ./admin
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {account}.dkr.ecr.us-east-1.amazonaws.com
docker tag admin-service:latest {account}.dkr.ecr.us-east-1.amazonaws.com/admin-service:latest
docker push {account}.dkr.ecr.us-east-1.amazonaws.com/admin-service:latest

# Update ECS service
aws ecs update-service --cluster YANTECH-cluster-dev --service YANTECH-admin-service-dev --force-new-deployment
```

## 📊 Monitoring

### CloudWatch Logs

```bash
# View admin service logs
aws logs tail /ecs/YANTECH-admin-dev --follow

# View requestor service logs
aws logs tail /ecs/YANTECH-requestor-dev --follow

# View worker service logs
aws logs tail /ecs/YANTECH-worker-dev --follow
```

### Metrics

- ECS service CPU/Memory utilization
- API Gateway request count and latency
- DynamoDB read/write capacity
- SQS queue depth and message age
- SES delivery metrics

## 🔧 Configuration

### Environment Variables

**Admin Service:**
```env
DYNAMODB_APPLICATIONS_TABLE=YANTECH-YNP01-AWS-DYNAMODB-APPLICATIONS-DEV
AWS_REGION=us-east-1
JWT_SECRET_PARAMETER=/yantech/dev/admin/jwt-secret
```

**Requestor Service:**
```env
DYNAMODB_REQUESTS_TABLE=YANTECH-YNP01-AWS-DYNAMODB-REQUESTS-DEV
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/{account}/yantech-notification-queue-dev
JWT_SECRET_PARAMETER=/yantech/dev/admin/jwt-secret
```

**Worker Service:**
```env
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/{account}/yantech-notification-queue-dev
DYNAMODB_REQUESTS_TABLE=YANTECH-YNP01-AWS-DYNAMODB-REQUESTS-DEV
AWS_REGION=us-east-1
```

## 🐛 Troubleshooting

### Common Issues

**Service Won't Start:**
- Check environment variables are set correctly
- Verify AWS credentials have necessary permissions
- Check DynamoDB tables exist
- Verify SQS queue is accessible

**Authentication Failures:**
- Verify API key is valid and active
- Check JWT secret is configured correctly
- Ensure application exists in DynamoDB

**Notification Delivery Issues:**
- Check SES domain verification status
- Verify SNS topic permissions
- Review CloudWatch logs for errors
- Check SQS dead letter queue

### Debug Commands

```bash
# Check DynamoDB tables
aws dynamodb list-tables

# Check SQS queue
aws sqs get-queue-attributes --queue-url {queue-url} --attribute-names All

# Test SES sending
aws ses send-email --from sender@example.com --to recipient@example.com --subject "Test" --text "Test message"
```

## 📖 API Documentation

### Admin API Endpoints

- `GET /apps` - List all applications
- `POST /app` - Create new application
- `PUT /app/{id}` - Update application
- `DELETE /app/{id}` - Delete application
- `GET /app/{id}/api-keys` - List API keys
- `POST /app/{id}/api-key` - Generate API key
- `DELETE /app/{id}/api-key/{key_id}` - Delete API key

### Requestor API Endpoints

- `POST /auth` - Authenticate and get JWT token
- `POST /notifications` - Send notification request
- `GET /health` - Health check endpoint

Interactive API documentation available at:
- Admin: http://localhost:8080/docs
- Requestor: http://localhost:80/docs

## 🔒 Security

- JWT-based authentication with expiration
- API key encryption at rest
- Secure parameter storage (AWS Systems Manager)
- VPC isolation for ECS services
- Security group restrictions
- HTTPS enforcement via API Gateway

## 📈 Performance

- Asynchronous notification processing via SQS
- Connection pooling for DynamoDB
- Efficient batch processing in worker
- Auto-scaling ECS services
- CloudWatch metrics for monitoring

## 📚 Documentation

- [Release Guide](./docs/RELEASE_GUIDE.md) - Creating releases and tags
- [Release Quick Reference](./RELEASE_QUICK_REFERENCE.md) - Quick commands
- [Testing Guide](./TESTING_GUIDE.md) - Running tests
- [Test Execution Summary](./TEST_EXECUTION_SUMMARY.md) - Test results

## 🏷️ Releases

**Current Version:** v1.0.0

**Creating a Release:**
```bash
# Windows
scripts\create-release.bat 1.0.0 "Release message"

# Linux/Mac
./scripts/create-release.sh 1.0.0 "Release message"
```

**Docker Images:**
- Production: `admin-prod:v1.0.0`, `requestor-prod:v1.0.0`, `worker-prod:v1.0.0`
- Branch: `admin-dev:{sha}-dev-{timestamp}`

See [releases page](https://github.com/YANTECH-NP/YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin/releases) for version history.

## 🤝 Contributing

1. Create feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Update documentation
5. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

---

**AWS Account**: 588082972397  
**Region**: us-east-1  
**Project Code**: YNP01  
**Version**: 1.0
