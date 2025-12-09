# Backend Release Quick Reference

## 🚀 Create Production Release

### Using Script (Recommended)

**Windows:**
```bash
scripts\create-release.bat 1.0.0 "Release message"
```

**Linux/Mac:**
```bash
./scripts/create-release.sh 1.0.0 "Release message"
```

### Manual Process

```bash
# 1. Checkout main and pull latest
git checkout main
git pull origin main

# 2. Run tests
./run-tests.sh

# 3. Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0

Services: admin, requestor, worker
Features: [list features]
Fixes: [list fixes]"

git push origin v1.0.0
```

---

## 🔧 Hotfix Release

```bash
# 1. Create hotfix branch
git checkout -b hotfix/v1.0.1 main

# 2. Make fixes and test
git add .
git commit -m "fix: critical bug"
./run-tests.sh

# 3. Merge to main
git checkout main
git merge hotfix/v1.0.1
git push origin main

# 4. Tag and push
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git push origin v1.0.1
```

---

## 📦 Feature Release

```bash
# 1. Merge feature to main
git checkout main
git pull origin main

# 2. Tag and push
git tag -a v1.1.0 -m "Release v1.1.0 - New features"
git push origin v1.1.0
```

---

## 🏷️ Version Numbers

| Type | Version | When to Use |
|------|---------|-------------|
| **MAJOR** | v2.0.0 | Breaking changes |
| **MINOR** | v1.1.0 | New features (backward compatible) |
| **PATCH** | v1.0.1 | Bug fixes |

---

## ✅ What Happens After Tag Push

1. ✅ GitHub Actions workflow triggered
2. ✅ Docker images built for all services
3. ✅ Images pushed to ECR with version tag
4. ✅ ECS task definitions updated
5. ✅ Services deployed to production ECS
6. ✅ Health checks performed
7. ✅ GitHub release created automatically

---

## 🐳 Docker Images Created

```
admin-prod:v1.0.0
requestor-prod:v1.0.0
worker-prod:v1.0.0
```

---

## 🔍 Verify Release

```bash
# Check GitHub Actions
https://github.com/YANTECH-NP/YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin/actions

# Check ECS Services
aws ecs describe-services --cluster YANTECH-cluster-prod \
  --services YANTECH-admin-service-prod

# Check Production APIs
curl https://admin.prod.api.project-dolphin.com/health
curl https://client.prod.api.project-dolphin.com/health

# View Logs
aws logs tail /ecs/YANTECH-admin-prod --follow

# Check Release
https://github.com/YANTECH-NP/YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin/releases
```

---

## 🛠️ Useful Commands

```bash
# List all tags
git tag

# Show tag details
git show v1.0.0

# Delete local tag (if needed)
git tag -d v1.0.0

# View recent tags
git tag --sort=-creatordate | head -n 5

# Check ECS cluster
aws ecs describe-clusters --clusters YANTECH-cluster-prod

# List running tasks
aws ecs list-tasks --cluster YANTECH-cluster-prod \
  --service-name YANTECH-admin-service-prod

# View service events
aws ecs describe-services --cluster YANTECH-cluster-prod \
  --services YANTECH-admin-service-prod \
  --query 'services[0].events[0:5]'
```

---

## 🔄 Rollback

```bash
# List task definition revisions
aws ecs list-task-definitions --family-prefix YANTECH-admin-prod

# Rollback to previous version
aws ecs update-service \
  --cluster YANTECH-cluster-prod \
  --service YANTECH-admin-service-prod \
  --task-definition YANTECH-admin-prod:PREVIOUS_REVISION \
  --force-new-deployment
```

---

## 📞 Troubleshooting

**Tag already exists:**
```bash
git tag -d v1.0.0
git push origin --delete v1.0.0
```

**Workflow not triggered:**
- Check tag format: `v*.*.*`
- Verify GitHub Actions enabled
- Check workflow file syntax

**ECS deployment failed:**
- Check cluster has EC2 instances
- Verify task definition is valid
- Review CloudWatch logs
- Check IAM permissions

**Service won't start:**
```bash
# Check logs
aws logs tail /ecs/YANTECH-admin-prod --since 10m

# Check stopped tasks
aws ecs list-tasks --cluster YANTECH-cluster-prod \
  --service-name YANTECH-admin-service-prod \
  --desired-status STOPPED
```

---

## 📚 Full Documentation

See [docs/RELEASE_GUIDE.md](./docs/RELEASE_GUIDE.md) for complete guide.

---

**Services:** Admin, Requestor, Worker  
**Cluster:** YANTECH-cluster-prod  
**Region:** us-east-1
