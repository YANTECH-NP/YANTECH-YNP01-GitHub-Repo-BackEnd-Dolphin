# Environment Promotion Workflow

## Overview

This guide explains how to promote code from development → staging → production.

---

## 🌳 Branch Strategy

```
develop  →  staging  →  main
  (dev)     (staging)   (prod)
```

**Branches:**
- `develop` - Development environment (auto-deploy to dev)
- `staging` - Staging environment (auto-deploy to staging)
- `main` - Production environment (auto-deploy to prod or use tags)

---

## 🚀 Initial Setup (One-Time)

### Create Staging Branch

**If staging branch doesn't exist:**

```bash
# 1. Checkout main
git checkout main
git pull origin main

# 2. Create staging from main
git checkout -b staging

# 3. Push staging to remote
git push -u origin staging

# 4. Return to develop
git checkout develop
```

**Verify branches exist:**
```bash
git branch -a
# Should show:
#   develop
#   staging
#   main
#   remotes/origin/develop
#   remotes/origin/staging
#   remotes/origin/main
```

---

## 📋 Daily Development Workflow

### 1. Feature Development (Dev Environment)

```bash
# Work on develop branch
git checkout develop
git pull origin develop

# Create feature branch (optional)
git checkout -b feature/my-feature

# Make changes
git add .
git commit -m "feat: add new feature"

# Push to develop (or merge feature branch to develop)
git checkout develop
git merge feature/my-feature
git push origin develop
```

**✅ Result:** Auto-deploys to dev environment
- Frontend: https://dev.admin-dashboard.project-dolphin.com
- Backend: https://admin.dev.api.project-dolphin.com

**Verify in dev:**
- Test functionality
- Check logs
- Verify no errors

---

### 2. Promote to Staging

**When ready to test in staging:**

```bash
# 1. Checkout staging
git checkout staging
git pull origin staging

# 2. Merge develop into staging
git merge develop

# 3. Resolve conflicts if any
# If conflicts occur:
#   - Edit conflicting files
#   - git add <resolved-files>
#   - git commit -m "Merge develop into staging"

# 4. Push to staging
git push origin staging
```

**✅ Result:** Auto-deploys to staging environment
- Frontend: https://staging.admin-dashboard.project-dolphin.com
- Backend: https://admin.staging.api.project-dolphin.com

**Verify in staging:**
- Run full test suite
- User acceptance testing (UAT)
- Performance testing
- Security checks

---

### 3. Promote to Production

**When staging is verified and approved:**

#### Option A: Direct Merge (Quick Deploy)

```bash
# 1. Checkout main
git checkout main
git pull origin main

# 2. Merge staging into main
git merge staging

# 3. Push to main
git push origin main
```

**✅ Result:** Auto-deploys to prod environment

#### Option B: Tagged Release (Recommended)

```bash
# 1. Merge staging to main
git checkout main
git pull origin main
git merge staging
git push origin main

# 2. Create release tag
git tag -a v1.0.0 -m "Release v1.0.0

Features:
- Feature 1
- Feature 2

Fixes:
- Bug fix 1
- Bug fix 2"

# 3. Push tag
git push origin v1.0.0
```

**✅ Result:** 
- Deploys to production
- Creates GitHub release
- Tags Docker images (backend)

**Verify in production:**
- Frontend: https://prod.admin-dashboard.project-dolphin.com
- Backend: https://admin.prod.api.project-dolphin.com

---

## 🔄 Complete Promotion Example

### Scenario: Deploy New Feature to Production

**Step 1: Develop Feature**
```bash
git checkout develop
git pull origin develop

# Make changes
git add .
git commit -m "feat: add notification templates"
git push origin develop

# Wait for dev deployment
# Test in dev environment
```

**Step 2: Promote to Staging**
```bash
git checkout staging
git pull origin staging
git merge develop
git push origin staging

# Wait for staging deployment
# Run UAT in staging
```

**Step 3: Promote to Production**
```bash
git checkout main
git pull origin main
git merge staging
git push origin main

# Create release tag
git tag -a v1.1.0 -m "Release v1.1.0 - Notification templates"
git push origin v1.1.0

# Wait for production deployment
# Verify in production
```

---

## 🔥 Hotfix Workflow

### Scenario: Critical Bug in Production

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. Fix the bug
git add .
git commit -m "fix: resolve critical authentication bug"

# 3. Merge to main
git checkout main
git merge hotfix/critical-bug
git push origin main

# 4. Create hotfix tag
git tag -a v1.0.1 -m "Hotfix v1.0.1 - Critical bug fix"
git push origin v1.0.1

# 5. Merge back to staging and develop
git checkout staging
git merge main
git push origin staging

git checkout develop
git merge main
git push origin develop

# 6. Delete hotfix branch
git branch -d hotfix/critical-bug
```

---

## 📊 Branch Protection Rules (Recommended)

### GitHub Settings → Branches → Branch Protection

**For `main` branch:**
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Include administrators

**For `staging` branch:**
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass

**For `develop` branch:**
- ✅ Require status checks to pass

---

## 🛡️ Best Practices

### DO

✅ Always test in dev before promoting to staging
✅ Run full test suite in staging
✅ Get approval before promoting to production
✅ Use tags for production releases
✅ Keep branches in sync (develop → staging → main)
✅ Document changes in commit messages
✅ Verify deployments after each promotion

### DON'T

❌ Skip staging environment
❌ Push directly to main without testing
❌ Merge main back to develop (except for hotfixes)
❌ Delete production tags
❌ Force push to protected branches
❌ Deploy on Fridays (unless necessary)

---

## 🔍 Verification Checklist

### After Dev Deployment
- [ ] Application loads without errors
- [ ] New features work as expected
- [ ] No console errors
- [ ] API endpoints respond correctly

### After Staging Deployment
- [ ] All dev checks passed
- [ ] Full test suite passed
- [ ] UAT completed
- [ ] Performance acceptable
- [ ] Security scan passed
- [ ] Stakeholder approval received

### After Production Deployment
- [ ] All staging checks passed
- [ ] Production URLs accessible
- [ ] No error spikes in logs
- [ ] Monitoring dashboards normal
- [ ] Rollback plan ready
- [ ] Team notified

---

## 🚨 Rollback Procedures

### Rollback Production

**Option 1: Revert Commit**
```bash
git checkout main
git revert HEAD
git push origin main
```

**Option 2: Rollback to Previous Tag**
```bash
# Frontend: Redeploy previous version
git checkout v1.0.0
# Trigger manual deployment

# Backend: Update ECS to previous task definition
aws ecs update-service \
  --cluster YANTECH-cluster-prod \
  --service YANTECH-admin-service-prod \
  --task-definition YANTECH-admin-prod:PREVIOUS_REVISION
```

---

## 📞 Troubleshooting

### Merge Conflicts

```bash
# When merge conflicts occur
git merge develop
# CONFLICT (content): Merge conflict in file.txt

# 1. View conflicts
git status

# 2. Edit conflicting files
# Look for <<<<<<< HEAD markers

# 3. Resolve conflicts
git add <resolved-files>
git commit -m "Resolve merge conflicts"
git push origin staging
```

### Deployment Failed

**Check GitHub Actions:**
1. Go to repository → Actions tab
2. Find failed workflow
3. Review error logs
4. Fix issues and re-push

**Check AWS Resources:**
```bash
# Frontend: Check S3 and CloudFront
aws s3 ls s3://yantech-ynp01-admin-dashboard-staging/
aws cloudfront get-distribution --id <DISTRIBUTION_ID>

# Backend: Check ECS services
aws ecs describe-services --cluster YANTECH-cluster-staging \
  --services YANTECH-admin-service-staging
```

---

## 📚 Quick Reference

### Promote Dev → Staging
```bash
git checkout staging && git pull origin staging
git merge develop
git push origin staging
```

### Promote Staging → Prod
```bash
git checkout main && git pull origin main
git merge staging
git push origin main
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Hotfix
```bash
git checkout -b hotfix/bug main
# Fix bug
git checkout main && git merge hotfix/bug
git push origin main
git tag -a v1.0.1 -m "Hotfix v1.0.1"
git push origin v1.0.1
```

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Maintained By**: YANTECH Development Team
