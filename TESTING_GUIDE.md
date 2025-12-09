# 🧪 YANTECH Backend Testing Guide

## Overview

This document describes the comprehensive testing framework implemented for the YANTECH notification platform backend services.

## 🏗️ Testing Architecture

### Test Types Implemented

1. **Unit Tests** - Test individual functions and methods
2. **Integration Tests** - Test service interactions and AWS integrations
3. **Regression Tests** - Ensure existing functionality remains intact
4. **Security Tests** - Static analysis and dependency vulnerability scanning
5. **End-to-End Tests** - Complete workflow validation

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── admin/
│   └── test_admin_service.py    # Admin service unit tests
├── requestor/
│   └── test_requestor_service.py # Requestor service unit tests
├── worker/
│   └── test_worker_service.py   # Worker service unit tests
└── integration/
    └── test_end_to_end.py       # Integration tests
```

## 🚀 Running Tests

### Prerequisites

```bash
# Install testing dependencies (already included in requirements.txt)
pip install pytest pytest-asyncio pytest-cov httpx moto faker
```

### Local Testing

```bash
# Run all tests
pytest

# Run specific service tests
pytest tests/admin/ -v
pytest tests/requestor/ -v
pytest tests/worker/ -v

# Run by test type
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m regression     # Regression tests only

# Run with coverage
pytest --cov=admin/app --cov=requestor/app --cov=worker/app --cov-report=html

# Run specific test
pytest tests/admin/test_admin_service.py::test_create_application -v
```

### CI/CD Testing

Tests run automatically on:
- **Push** to main, dev, staging branches
- **Pull Requests** to main, dev, staging branches
- **Manual trigger** via GitHub Actions

## 📊 Test Coverage

### Current Coverage Targets

- **Minimum Coverage**: 80%
- **Unit Tests**: All core functions
- **Integration Tests**: Critical workflows
- **Regression Tests**: Key business logic

### Coverage Reports

- **HTML Report**: `htmlcov/index.html` (local)
- **XML Report**: `coverage.xml` (CI/CD)
- **Terminal**: Real-time coverage during test runs

## 🔧 Test Configuration

### pytest.ini Configuration

```ini
[tool:pytest]
testpaths = tests
addopts = --strict-markers --verbose --cov-fail-under=80
asyncio_mode = auto
markers =
    unit: Unit tests
    integration: Integration tests
    regression: Regression tests
    slow: Slow running tests
    aws: Tests requiring AWS services
```

### Environment Variables

Tests use isolated test environment:
```bash
AWS_REGION=us-east-1
APPLICATIONS_TABLE=test-applications
API_KEYS_TABLE=test-api-keys
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/test-queue
ALLOWED_ORIGINS=*
```

## 🎯 Test Categories

### Unit Tests

**Purpose**: Test individual functions in isolation
**Mocking**: AWS services, database calls, external dependencies
**Speed**: Fast (< 1 second per test)

**Examples**:
- API endpoint responses
- Data validation
- Business logic functions
- Error handling

### Integration Tests

**Purpose**: Test service interactions and AWS integrations
**Mocking**: Uses moto for AWS service simulation
**Speed**: Medium (1-5 seconds per test)

**Examples**:
- Complete notification workflow
- Database CRUD operations
- SQS message processing
- Multi-service interactions

### Regression Tests

**Purpose**: Ensure existing functionality doesn't break
**Focus**: Critical business logic and API contracts
**Trigger**: Every code change

**Examples**:
- API key format consistency
- Email fallback behavior
- Request/response formats
- Authentication flows

### Security Tests

**Purpose**: Identify security vulnerabilities and dependency issues
**Tools**: Bandit (SAST), Safety (dependency check), CodeQL
**Frequency**: Every push + weekly scheduled scans

**Coverage**:
- SQL injection detection
- Hardcoded secrets
- Insecure cryptography
- Vulnerable dependencies

## 🔄 Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test-suite.yml
- Unit tests (parallel by service)
- Integration tests
- Security scans
- Coverage reporting
- Test result summary
```

### Test Pipeline Stages

1. **Setup** - Install dependencies, cache pip packages
2. **Unit Tests** - Run service-specific unit tests in parallel
3. **Regression Tests** - Validate critical functionality
4. **Integration Tests** - End-to-end workflow validation
5. **Security Tests** - Static analysis and dependency checks
6. **Reporting** - Coverage reports and test summaries

### Failure Handling

- **Unit Test Failure**: Blocks PR merge
- **Integration Test Failure**: Blocks deployment
- **Security Test Failure**: Creates security advisory
- **Coverage Below 80%**: Fails CI pipeline

## 📝 Writing New Tests

### Unit Test Template

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.unit
def test_function_name():
    """Test description."""
    # Arrange
    # Act
    # Assert
    pass

@pytest.mark.regression
def test_existing_behavior():
    """Regression test: Ensure behavior remains consistent."""
    # Test critical functionality that shouldn't change
    pass
```

### Integration Test Template

```python
import pytest
from moto import mock_dynamodb, mock_sqs

@pytest.mark.integration
@mock_dynamodb
@mock_sqs
def test_integration_scenario(aws_credentials):
    """Test service integration."""
    # Setup AWS mocks
    # Test complete workflow
    # Verify results
    pass
```

### Test Naming Convention

- `test_[function_name]` - Basic functionality test
- `test_[function_name]_error_handling` - Error case test
- `test_[feature]_regression` - Regression test
- `test_[workflow]_integration` - Integration test

## 🚨 Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Add service directories to Python path
export PYTHONPATH="${PYTHONPATH}:./admin:./requestor:./worker"
```

**AWS Credential Errors**:
```bash
# Ensure moto mocks are properly configured
@pytest.fixture(scope="session")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
```

**Slow Tests**:
```bash
# Run only fast tests during development
pytest -m "not slow"
```

### Debug Mode

```bash
# Run with detailed output
pytest -v --tb=long --capture=no

# Run single test with debugging
pytest tests/admin/test_admin_service.py::test_create_application -v -s
```

## 📈 Test Metrics

### Success Criteria

- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ Coverage ≥ 80%
- ✅ No security vulnerabilities
- ✅ No regression failures

### Performance Targets

- **Unit Tests**: < 30 seconds total
- **Integration Tests**: < 2 minutes total
- **Full Test Suite**: < 5 minutes total

## 🔮 Future Enhancements

### Planned Additions

1. **Load Testing** - Performance and stress testing
2. **Contract Testing** - API contract validation
3. **Chaos Testing** - Failure scenario testing
4. **Visual Testing** - UI component testing (if applicable)
5. **Database Migration Testing** - Schema change validation

### Tools to Consider

- **Locust** - Load testing
- **Pact** - Contract testing
- **Chaos Monkey** - Chaos engineering
- **TestContainers** - Real service testing

## 📞 Support

For testing issues or questions:
1. Check this documentation
2. Review test logs in GitHub Actions
3. Run tests locally with verbose output
4. Check mocking configuration in `conftest.py`

## 🎯 Summary

This testing framework provides:
- **Comprehensive coverage** of all services
- **Automated execution** in CI/CD pipeline
- **Regression protection** for critical functionality
- **Security validation** through static analysis
- **Fast feedback** for developers
- **Quality gates** for deployments

The framework ensures code quality, prevents regressions, and maintains security standards across the YANTECH notification platform.