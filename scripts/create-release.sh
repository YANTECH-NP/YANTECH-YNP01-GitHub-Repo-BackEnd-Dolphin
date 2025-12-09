#!/bin/bash

# YANTECH Backend Release Script
# Usage: ./scripts/create-release.sh <version> [message]
# Example: ./scripts/create-release.sh 1.0.0 "Initial production release"

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if version is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Version number required${NC}"
    echo "Usage: ./scripts/create-release.sh <version> [message]"
    echo "Example: ./scripts/create-release.sh 1.0.0 \"Initial release\""
    exit 1
fi

VERSION=$1
TAG="v${VERSION}"
MESSAGE=${2:-"Release ${TAG}"}

echo -e "${YELLOW}Creating backend release ${TAG}...${NC}"

# Verify we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}Error: Must be on main branch (currently on ${CURRENT_BRANCH})${NC}"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}Error: Uncommitted changes detected${NC}"
    echo "Please commit or stash your changes first"
    exit 1
fi

# Pull latest changes
echo -e "${YELLOW}Pulling latest changes...${NC}"
git pull origin main

# Check if tag already exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo -e "${RED}Error: Tag ${TAG} already exists${NC}"
    exit 1
fi

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
if [ -f "./run-tests.sh" ]; then
    ./run-tests.sh || { echo -e "${RED}Tests failed${NC}"; exit 1; }
else
    echo -e "${YELLOW}No test script found, skipping tests${NC}"
fi

# Verify Docker builds
echo -e "${YELLOW}Verifying Docker builds...${NC}"
for SERVICE in admin requestor worker; do
    if [ -d "./$SERVICE" ]; then
        echo "Building $SERVICE..."
        docker build -t ${SERVICE}-test:${VERSION} ./$SERVICE || {
            echo -e "${RED}Docker build failed for $SERVICE${NC}"
            exit 1
        }
    fi
done

# Create tag
echo -e "${YELLOW}Creating tag ${TAG}...${NC}"
git tag -a "$TAG" -m "$MESSAGE"

# Push tag
echo -e "${YELLOW}Pushing tag to GitHub...${NC}"
git push origin "$TAG"

echo -e "${GREEN}✅ Release ${TAG} created successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Monitor GitHub Actions: https://github.com/YANTECH-NP/YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin/actions"
echo "2. Check ECS deployment: aws ecs describe-services --cluster YANTECH-cluster-prod --services YANTECH-admin-service-prod"
echo "3. Verify APIs: curl https://admin.prod.api.project-dolphin.com/health"
echo "4. Check release: https://github.com/YANTECH-NP/YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin/releases"
echo ""
echo "Docker images will be tagged as:"
echo "  - admin-prod:${TAG}"
echo "  - requestor-prod:${TAG}"
echo "  - worker-prod:${TAG}"
