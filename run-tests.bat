@echo off
REM YANTECH Backend Test Runner for Windows
REM Run all tests locally with proper setup

echo 🧪 YANTECH Backend Test Suite
echo ==============================

REM Check Python version
echo 📋 Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.11+
    exit /b 1
)

REM Set environment variables
echo 🔧 Setting up environment...
set PYTHONPATH=%PYTHONPATH%;.\admin;.\requestor;.\worker
set AWS_ACCESS_KEY_ID=testing
set AWS_SECRET_ACCESS_KEY=testing
set AWS_REGION=us-east-1

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r admin/requirements.txt --quiet
pip install -r requestor/requirements.txt --quiet
pip install -r worker/requirements.txt --quiet

REM Clear pytest cache
echo 🧹 Clearing pytest cache...
pytest --cache-clear >nul 2>&1

REM Run tests based on argument
set TEST_TYPE=%1
if "%TEST_TYPE%"=="" set TEST_TYPE=all

if "%TEST_TYPE%"=="unit" (
    echo 🚀 Running unit tests...
    pytest -m unit -v --tb=short
) else if "%TEST_TYPE%"=="integration" (
    echo 🔗 Running integration tests...
    pytest -m integration -v --tb=short
) else if "%TEST_TYPE%"=="regression" (
    echo 🔄 Running regression tests...
    pytest -m regression -v --tb=short
) else if "%TEST_TYPE%"=="coverage" (
    echo 📊 Running tests with coverage...
    pytest --cov=admin/app --cov=requestor/app --cov=worker/app --cov-report=html --cov-report=term-missing -v
    echo 📋 Coverage report generated: htmlcov/index.html
) else if "%TEST_TYPE%"=="fast" (
    echo ⚡ Running fast tests only...
    pytest -m "unit or regression" -v --tb=short
) else if "%TEST_TYPE%"=="security" (
    echo 🔒 Running security tests...
    pip install bandit safety --quiet
    echo Running Bandit security scan...
    bandit -r admin/ requestor/ worker/ -f json -o bandit-report.json
    echo Running Safety dependency check...
    safety check --json --output safety-report.json
    echo Security reports generated: bandit-report.json, safety-report.json
) else if "%TEST_TYPE%"=="all" (
    echo 🎯 Running complete test suite...
    pytest -v --tb=short --cov=admin/app --cov=requestor/app --cov=worker/app --cov-report=html
    echo 📋 Coverage report: htmlcov/index.html
) else (
    echo Usage: %0 [unit^|integration^|regression^|coverage^|fast^|security^|all]
    echo.
    echo Options:
    echo   unit        - Run unit tests only
    echo   integration - Run integration tests only
    echo   regression  - Run regression tests only
    echo   coverage    - Run all tests with detailed coverage
    echo   fast        - Run unit + regression tests ^(quick^)
    echo   security    - Run security scans
    echo   all         - Run complete test suite ^(default^)
    exit /b 1
)

if %errorlevel% equ 0 (
    echo ✅ Tests completed successfully!
) else (
    echo ❌ Tests failed!
    exit /b 1
)