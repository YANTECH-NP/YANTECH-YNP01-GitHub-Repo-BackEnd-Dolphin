#!/bin/bash
set -e

echo "YANTECH Backend Test Suite"
echo "=============================="

# 1. Force virtualenv + reuse it
VENV=".venv"
if [ ! -d "$VENV" ]; then
    echo "Creating virtualenv..."
    python3 -m venv $VENV
fi
source $VENV/bin/activate

# Upgrade pip once
pip install --upgrade pip setuptools wheel --quiet

# 2. Install all deps exactly once (deduped + cached)
echo "Installing dependencies (cached)..."
cat admin/requirements.txt requestor/requirements.txt worker/requirements.txt | sort -u > /tmp/reqs.txt
pip install -r /tmp/reqs.txt --quiet
pip install "moto[all]>=4.2.0" pytest pytest-cov pytest-asyncio faker --quiet

rm /tmp/reqs.txt

# 3. Set testing mode
export TESTING=true
export PYTHONPATH="${PYTHONPATH}:./admin:./requestor:./worker"

case "${1:-all}" in
    "all"|"")
        echo "Running full suite with coverage..."
        pytest -v --tb=short --cov=admin/app --cov=requestor/app --cov=worker/app --cov-report=term-missing --cov-report=html
        echo "Coverage → htmlcov/index.html"
        ;;
    "fast")
        pytest -m "unit or regression" -v --tb=short
        ;;
    *)
        pytest "$@"
        ;;
esac

echo "All done!"