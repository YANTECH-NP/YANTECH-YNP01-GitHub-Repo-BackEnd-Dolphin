# Release Guide - YANTECH Backend Services

## Overview

This guide explains how to create releases for the YANTECH Backend microservices (Admin, Requestor, Worker) using Git tags and automated ECS deployment.

---

## 🏷️ Tagging Strategy

### Production Releases (Semantic Versioning)

**Format:** `vMAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (v1.x.x → v2.0.0)
- **MINOR**: New features, backward compatible (v1.0.x → v1.1.0)
- **PATCH**: Bug fixes (v1.0.0 → v1.0.1)

**Examples:**
- `v1.0.0` - Initial production release
- `v1.0.1` - Bug fix release
- `v1.1.0` - New feature release
- `v2.0.0` - Major version with breaking changes

### Branch Deployments (Automatic)

**Format:** `{commit-sha}-{environment}-{timestamp}`

**Examples:**
- `a1b2c3d-dev-20241204-143052` - Dev deployment
- `x9y8z7w-staging-20241204-143052` - Staging deployment

**Triggered by:**
- Push to `dev` branch → Deploy to dev
- Push to `staging` branch → Deploy to staging

---

## 🚀 Creating a Production Release

### Step 1: Prepare the Release

**1. Ensure all changes are merged to main:**
```bash
git checkout main
git pull origin main
```

**2. Run tests locally:**
```bash
# Run all tests
./run-tests.sh

# Or on Windows
run-tests.bat
```

**3. Verify services build:**
```bash
# Test build each service
docker build -t admin-test ./admin
docker build -t requestor-test ./requestor
docker build -t worker-test ./worker
```

### Step 2: Create the Tag

**Create annotated tag with detailed message:**
```bash
git tag -a v1.0.0 -m "Release v1.0.0

Services:
- Admin Service: Application and API key management
- Requestor Service: Notification request processing
- Worker Service: Notification delivery

Features:
- Multi-channel notifications (Email, SMS, Push)
- JWT authentication with API keys
- DynamoDB integration
- SQS message queuing
- Automatic retry logic

Fixes:
- Improved error handling in worker
- Fixed authentication token refresh
- Enhanced logging for debugging

Breaking Changes:
- None (initial release)

Deployment:
- ECS Cluster: YANTECH-cluster-prod
- Launch Type: EC2
- Services: admin-prod, requestor-prod, worker-prod"
```

### Step 3: Push the Tag

```bash
git push origin v1.0.0
```

**This will automatically:**
1. Trigger GitHub Actions workflow
2. Build Docker images for all services
3. Push images to ECR with tag `v1.0.0`
4. Update ECS task definitions
5. Deploy to production ECS cluster
6. Wait for deployment completion
7. Create GitHub release with notes

### Step 4: Monitor Deployment

**1. Check GitHub Actions:**
```
https://github.com/YANTECH-NP/YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin/actions
```

**2. Monitor ECS Services:**
```bash
# Check cluster status
aws ecs describe-clusters --clusters YANTECH-cluster-prod

# Check service status
aws ecs describe-services --cluster YANTECH-cluster-prod \
  --services YANTECH-admin-service-prod YANTECH-requestor-service-prod YANTECH-worker-service-prod
```

**3. View logs:**
```bash
# Admin service logs
aws logs tail /ecs/YANTECH-admin-prod --follow

# Requestor service logs
aws logs tail /ecs/YANTECH-requestor-prod --follow

# Worker service logs
aws logs tail /ecs/YANTECH-worker-prod --follow
```

### Step 5: Verify Deployment

**Test endpoints:**
```bash
# Admin API health check
curl https://admin.prod.api.project-dolphin.com/health

# Requestor API health check
curl https://client.prod.api.project-dolphin.com/health
```

---

## 🔧 Creating a Hotfix Release

### Scenario: Critical bug in production

**1. Create hotfix branch from main:**
```bash
git checkout main
git pull origin main
git checkout -b hotfix/v1.0.1
```

**2. Make the fix:**
```bash
# Edit files to fix the bug
# Example: Fix in admin service
vim admin/app/main.py

git add .
git commit -m "fix: resolve critical authentication bug

- Fixed token expiration handling in admin service
- Added retry logic for DynamoDB operations
- Improved error messages"
```

**3. Test the fix:**
```bash
# Run tests
./run-tests.sh

# Test specific service
pytest tests/admin/ -v
```

**4. Merge to main:**
```bash
git checkout main
git merge hotfix/v1.0.1
git push origin main
```

**5. Create hotfix tag:**
```bash
git tag -a v1.0.1 -m "Hotfix v1.0.1

Critical Fixes:
- Fixed authentication token expiration bug in admin service
- Added retry logic for DynamoDB throttling
- Improved error handling in worker service

Services Updated:
- admin-prod:v1.0.1
- requestor-prod:v1.0.1
- worker-prod:v1.0.1

Impact: High
Urgency: Critical
Tested: Yes"

git push origin v1.0.1
```

**6. Clean up:**
```bash
git branch -d hotfix/v1.0.1
```

---

## 📦 Creating a Feature Release

### Scenario: New feature ready for production

**1. Ensure feature is merged to main:**
```bash
git checkout main
git pull origin main
```

**2. Create feature release tag:**
```bash
git tag -a v1.1.0 -m "Release v1.1.0

New Features:
- Batch notification processing in worker
- Enhanced API key management with expiration
- Real-time notification status tracking
- Webhook callbacks for delivery status

Improvements:
- Optimized DynamoDB queries
- Reduced Lambda cold starts
- Better error handling and logging
- Enhanced monitoring metrics

Bug Fixes:
- Fixed SQS message visibility timeout
- Resolved race condition in worker
- Fixed timezone handling in scheduler

Services Updated:
- admin-prod:v1.1.0
- requestor-prod:v1.1.0
- worker-prod:v1.1.0"

git push origin v1.1.0
```

---

## 🔄 Release Workflow

### Automated Process (via GitHub Actions)

```
Tag Push (v1.0.0)
    ↓
GitHub Actions Triggered
    ↓
┌─────────────────────────┐
│  Build Docker Images    │
│  - admin-prod:v1.0.0    │
│  - requestor-prod:v1.0.0│
│  - worker-prod:v1.0.0   │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  Push to ECR            │
│  - Tag with version     │
│  - Update latest        │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  Update Task Defs       │
│  - New image references │
│  - Register new revision│
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  Deploy to ECS          │
│  - Update services      │
│  - Force new deployment │
│  - Wait for healthy     │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  Create GitHub Release  │
│  - Release notes        │
│  - Docker image tags    │
│  - Deployment summary   │
└─────────────────────────┘
```

---

## 📋 Release Checklist

### Pre-Release

- [ ] All features tested in staging
- [ ] All tests passing (`./run-tests.sh`)
- [ ] Docker images build successfully
- [ ] No known critical bugs
- [ ] Database migrations completed (if any)
- [ ] Environment variables updated (if needed)
- [ ] Stakeholder approval received
- [ ] Rollback plan prepared

### Release

- [ ] Tag created with proper version
- [ ] Tag pushed to GitHub
- [ ] GitHub Actions workflow completed
- [ ] Docker images pushed to ECR
- [ ] ECS services updated
- [ ] All services healthy
- [ ] GitHub release created

### Post-Release

- [ ] Production APIs verified
- [ ] Smoke tests passed
- [ ] CloudWatch metrics normal
- [ ] No error spikes in logs
- [ ] Team notified
- [ ] Documentation updated
- [ ] Release announcement sent

---

## 🛠️ Managing Tags

### List All Tags

```bash
# Local tags
git tag

# Remote tags
git ls-remote --tags origin

# Tags with messages
git tag -n

# Recent tags
git tag --sort=-creatordate | head -n 10
```

### View Tag Details

```bash
# Show tag information
git show v1.0.0

# Show commit for tag
git rev-list -n 1 v1.0.0

# Compare tags
git diff v1.0.0 v1.1.0
```

### Delete Tags (Use with Caution)

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag (DANGEROUS - avoid in production)
git push origin --delete v1.0.0
```

**⚠️ Warning:** Never delete production tags. They are immutable references.

---

## 🔍 Troubleshooting

### Tag Already Exists

**Error:** `fatal: tag 'v1.0.0' already exists`

**Solution:**
```bash
# Check if tag exists
git tag -l v1.0.0

# View tag details
git show v1.0.0

# If you need to recreate (not recommended for production)
git tag -d v1.0.0
git push origin --delete v1.0.0
git tag -a v1.0.0 -m "New message"
git push origin v1.0.0
```

### Workflow Not Triggered

**Check:**
1. Tag format matches `v*.*.*` pattern
2. Workflow file has tag trigger configured
3. GitHub Actions is enabled
4. Check Actions tab for errors

### Docker Build Failed

**Check:**
1. Dockerfile syntax is correct
2. All dependencies are available
3. Base images are accessible
4. Build context is correct

**Debug:**
```bash
# Build locally with verbose output
docker build --no-cache -t test-image ./admin

# Check build logs
docker build -t test-image ./admin 2>&1 | tee build.log
```

### ECS Deployment Failed

**Check:**
1. ECS cluster is active
2. EC2 instances are registered
3. Task definition is valid
4. IAM roles have correct permissions
5. Security groups allow traffic

**Debug:**
```bash
# Check cluster status
aws ecs describe-clusters --clusters YANTECH-cluster-prod

# Check service events
aws ecs describe-services --cluster YANTECH-cluster-prod \
  --services YANTECH-admin-service-prod \
  --query 'services[0].events[0:5]'

# Check task failures
aws ecs list-tasks --cluster YANTECH-cluster-prod \
  --service-name YANTECH-admin-service-prod \
  --desired-status STOPPED
```

### Service Won't Start

**Check CloudWatch logs:**
```bash
# View recent logs
aws logs tail /ecs/YANTECH-admin-prod --since 10m

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/YANTECH-admin-prod \
  --filter-pattern "ERROR"
```

**Common issues:**
- Environment variables missing
- Database connection failed
- Port conflicts
- Insufficient memory/CPU
- IAM permission issues

---

## 📊 Docker Image Tagging

### Production Tags (Semantic Versioning)

```
ECR Repository: {account}.dkr.ecr.us-east-1.amazonaws.com/admin-prod

Tags:
- v1.0.0 (specific version)
- v1.0 (minor version)
- v1 (major version)
- latest (most recent)
```

### Branch Tags (Automatic)

```
ECR Repository: {account}.dkr.ecr.us-east-1.amazonaws.com/admin-dev

Tags:
- a1b2c3d-dev-20241204-143052 (unique per build)
```

### Benefits

✅ **Traceability**: Know exactly what code is running
✅ **Rollback**: Easy to revert to previous versions
✅ **Audit**: Complete deployment history
✅ **No conflicts**: Unique tags per environment

---

## 🎯 Best Practices

### DO

✅ Use semantic versioning for production
✅ Write detailed tag messages
✅ Test thoroughly before tagging
✅ Tag from main branch only
✅ Use annotated tags (`-a` flag)
✅ Document breaking changes
✅ Monitor deployments
✅ Keep rollback plan ready

### DON'T

❌ Delete or move production tags
❌ Tag without testing
❌ Use lightweight tags for releases
❌ Skip version numbers
❌ Tag from feature branches
❌ Forget to push tags
❌ Deploy without approval

---

## 📞 Support

### Questions?

- Check workflow logs in GitHub Actions
- Review ECS service events
- Check CloudWatch logs
- Contact DevOps team
- Create GitHub issue

### Useful Commands

```bash
# Quick release (use script)
./scripts/create-release.sh 1.0.0

# View recent tags
git tag --sort=-creatordate | head -n 5

# Check ECS deployment
aws ecs describe-services --cluster YANTECH-cluster-prod \
  --services YANTECH-admin-service-prod

# View service logs
aws logs tail /ecs/YANTECH-admin-prod --follow

# Rollback to previous version
aws ecs update-service --cluster YANTECH-cluster-prod \
  --service YANTECH-admin-service-prod \
  --task-definition YANTECH-admin-prod:PREVIOUS_REVISION
```

---

## 🔄 Rollback Procedure

### If Deployment Fails

**1. Identify the issue:**
```bash
# Check service events
aws ecs describe-services --cluster YANTECH-cluster-prod \
  --services YANTECH-admin-service-prod

# Check logs
aws logs tail /ecs/YANTECH-admin-prod --since 10m
```

**2. Rollback to previous version:**
```bash
# List task definition revisions
aws ecs list-task-definitions --family-prefix YANTECH-admin-prod

# Update service to previous revision
aws ecs update-service \
  --cluster YANTECH-cluster-prod \
  --service YANTECH-admin-service-prod \
  --task-definition YANTECH-admin-prod:PREVIOUS_REVISION \
  --force-new-deployment
```

**3. Verify rollback:**
```bash
# Check service status
aws ecs describe-services --cluster YANTECH-cluster-prod \
  --services YANTECH-admin-service-prod \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'
```

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Maintained By**: YANTECH Development Team
