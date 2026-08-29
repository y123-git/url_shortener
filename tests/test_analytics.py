"""
Analytics Tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analytics():
    """Test analytics endpoint."""
    # First shorten
    response = client.post(
        "/shorten",
        json={"original_url": "https://example.com"}
    )
    data = response.json()
    code = data["short_code"]
    
    # Get analytics
    response = client.get(f"/analytics/{code}")
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == code

def test_analytics_not_found():
    """Test analytics not found."""
    response = client.get("/analytics/nonexistent")
    assert response.status_code == 404