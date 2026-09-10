"""
Shorten Tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_shorten_url():
    """Test URL shortening."""
    response = client.post(
        "/shorten",
        json={"original_url": "https://example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert "short_code" in data

def test_custom_code():
    """Test custom code."""
    response = client.post(
        "/shorten",
        json={
            "original_url": "https://github.com",
            "custom_code": "github"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == "github"

def test_invalid_custom_code():
    """Test invalid custom code."""
    response = client.post(
        "/shorten",
        json={
            "original_url": "https://example.com",
            "custom_code": "ab"  # Too short
        }
    )
    assert response.status_code == 400

def test_invalid_url_is_not_shortened():
    """Reject malformed URLs before a short code can be reserved."""
    response = client.post(
        "/shorten",
        json={
            "original_url": "https://invalid",
            "custom_code": "invalidurl"
        }
    )
    assert response.status_code == 400

    response = client.post(
        "/shorten",
        json={
            "original_url": "https://example.com",
            "custom_code": "invalidurl"
        }
    )
    assert response.status_code == 200

def test_ttl():
    """Test TTL."""
    response = client.post(
        "/shorten",
        json={
            "original_url": "https://example.com",
            "ttl_seconds": 3600
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["expires_at"] is not None