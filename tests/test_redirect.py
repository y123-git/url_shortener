"""
Redirect Tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_redirect():
    """Test redirect."""
    # First shorten
    response = client.post(
        "/shorten",
        json={"original_url": "https://example.com"}
    )
    data = response.json()
    code = data["short_code"]
    
    # Then redirect
    response = client.get(f"/{code}", allow_redirects=False)
    assert response.status_code == 301

def test_redirect_not_found():
    """Test redirect not found."""
    response = client.get("/nonexistent", allow_redirects=False)
    assert response.status_code == 404