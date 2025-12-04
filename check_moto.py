#!/usr/bin/env python3
"""Check moto imports to see what's available."""

try:
    import moto
    print(f"Moto version: {moto.__version__}")
    print("Available in moto module:")
    print([attr for attr in dir(moto) if 'mock' in attr.lower()])
    
    # Try different import patterns
    patterns = [
        "from moto import mock_dynamodb",
        "from moto.mock_dynamodb import mock_dynamodb", 
        "from moto.dynamodb import mock_dynamodb",
        "from moto import mock_aws",
    ]
    
    for pattern in patterns:
        try:
            exec(pattern)
            print(f"✅ {pattern}")
        except ImportError as e:
            print(f"❌ {pattern} - {e}")
            
except ImportError as e:
    print(f"Moto not installed: {e}")