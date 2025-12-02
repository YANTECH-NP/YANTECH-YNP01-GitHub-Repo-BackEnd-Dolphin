# Worker Service

The `worker` service polls messages from an AWS SQS queue, routes them based on the `OutputType`, and logs each processed notification to DynamoDB.

It is OIDC-enabled for secure deployments using GitHub Actions (no static AWS credentials needed).

---

## 🔧 Features

- Polls messages from AWS SQS
- Dispatches to appropriate handler (`SMS`, `EMAIL`, `PUSH`)
- Logs notification data + status to DynamoDB
- IAM Role OIDC support (no AWS credentials in code or .env)
- Containerized for ECS / GitHub CI

---

## 🗂 Folder Structure

worker/
├── app/
│ ├── init.py
│ ├── config.py # Loads env vars
│ ├── main.py # Polling loop + dispatcher
│ ├── handlers.py # SMS, EMAIL, PUSH logic
│ ├── sqs_client.py # SQS poller + deleter
│ └── db.py # DynamoDB writer
├── requirements.txt
├── Dockerfile
├── .env.example # Optional for local runs
└── README.md


---

## 🛠 Prerequisites

- AWS SQS Queue (Standard or FIFO)
- DynamoDB Table (e.g. `NotificationLogs`)
- IAM Role with:
  - `sqs:ReceiveMessage`, `sqs:DeleteMessage`
  - `dynamodb:PutItem`
- GitHub repo with:
  - Actions → **OIDC enabled**
  - Repo → Settings → Actions → Variables:
    - `AWS_REGION`
    - `SQS_QUEUE_URL`
    - `DYNAMODB_TABLE`

---

## 📦 Setup

### 1. GitHub Actions Variables

Go to your repo → Settings → **Actions → Variables**:

| Variable Name      | Example Value                                           |
|--------------------|--------------------------------------------------------|
| `AWS_REGION`       | `us-east-1`                                             |
| `SQS_QUEUE_URL`    | `https://sqs.us-east-1.amazonaws.com/1234567890/queue` |
| `DYNAMODB_TABLE`   | `NotificationLogs`                                      |

---

### 2. GitHub Actions Permissions

In your workflow file:
```yaml
permissions:
  id-token: write
  contents: read


