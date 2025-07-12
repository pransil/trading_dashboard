#!/usr/bin/env python3
"""Debug script to test API and see actual errors"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tests.conftest import test_app, db_session, sample_stock_data
from fastapi.testclient import TestClient
import pytest

def test_debug():
    # Create fixtures manually
    with db_session() as db:
        with sample_stock_data(db, None) as stock_data:  # This might not work, let me fix
            app = test_app()
            
            def override_get_db():
                yield db
            
            from models.database import get_db
            app.dependency_overrides[get_db] = override_get_db
            
            client = TestClient(app)
            response = client.get("/api/data/TSLA")
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            print(f"Headers: {response.headers}")

if __name__ == "__main__":
    test_debug()