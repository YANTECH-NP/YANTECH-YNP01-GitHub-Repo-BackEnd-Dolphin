@echo off
REM YANTECH Backend Release Script (Windows)
REM Usage: scripts\create-release.bat <version> [message]
REM Example: scripts\create-release.bat 1.0.0 "Initial production release"

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Error: Version number required
    echo Usage: scripts\create-release.bat ^<version^> [message]
    echo Example: scripts\create-release.bat 1.0.0 "Initial release"
    exit /b 1
)

set VERSION=%1
set TAG=v%VERSION%
set MESSAGE=%~2
if "%MESSAGE%"=="" set MESSAGE=Release %TAG%

echo Creating backend release %TAG%...

REM Verify we're on main branch
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
if not "%CURRENT_BRANCH%"=="main" (
    echo Error: Must be on main branch (currently on %CURRENT_BRANCH%)
    exit /b 1
)

REM Check for uncommitted changes
git diff-index --quiet HEAD --
if errorlevel 1 (
    echo Error: Uncommitted changes detected
    echo Please commit or stash your changes first
    exit /b 1
)

REM Pull latest changes
echo Pulling latest changes...
git pull origin main

REM Check if tag already exists
git rev-parse %TAG% >nul 2>&1
if not errorlevel 1 (
    echo Error: Tag %TAG% already exists
    exit /b 1
)

REM Run tests
echo Running tests...
if exist "run-tests.bat" (
    call run-tests.bat
    if errorlevel 1 (
        echo Tests failed
        exit /b 1
    )
) else (
    echo No test script found, skipping tests
)

REM Verify Docker builds
echo Verifying Docker builds...
for %%S in (admin requestor worker) do (
    if exist "%%S" (
        echo Building %%S...
        docker build -t %%S-test:%VERSION% .\%%S
        if errorlevel 1 (
            echo Docker build failed for %%S
            exit /b 1
        )
    )
)

REM Create tag
echo Creating tag %TAG%...
git tag -a "%TAG%" -m "%MESSAGE%"

REM Push tag
echo Pushing tag to GitHub...
git push origin "%TAG%"

echo.
echo ✅ Release %TAG% created successfully!
echo.
echo Next steps:
echo 1. Monitor GitHub Actions: https://github.com/YANTECH-NP/YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin/actions
echo 2. Check ECS deployment: aws ecs describe-services --cluster YANTECH-cluster-prod --services YANTECH-admin-service-prod
echo 3. Verify APIs: curl https://admin.prod.api.project-dolphin.com/health
echo 4. Check release: https://github.com/YANTECH-NP/YANTECH-YNP01-GitHub-Repo-BackEnd-Dolphin/releases
echo.
echo Docker images will be tagged as:
echo   - admin-prod:%TAG%
echo   - requestor-prod:%TAG%
echo   - worker-prod:%TAG%

endlocal
