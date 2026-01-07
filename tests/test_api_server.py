"""
API Server Tests
================
Tests for the ETL API server endpoints.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestAPIImports:
    """Test that API modules import correctly."""
    
    def test_flask_available(self):
        """Flask should be installed."""
        import flask
        assert flask is not None
    
    def test_flask_cors_available(self):
        """Flask-CORS should be installed."""
        import flask_cors
        assert flask_cors is not None
    
    def test_api_server_imports(self):
        """API server module should import without errors."""
        from src.api.server import app, get_orchestrator
        assert app is not None
        assert get_orchestrator is not None
    
    def test_app_is_flask_instance(self):
        """App should be a Flask instance."""
        from src.api.server import app
        from flask import Flask
        assert isinstance(app, Flask)


class TestAPIEndpointDefinitions:
    """Test that all expected endpoints are defined."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.api.server import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_endpoint_exists(self, client):
        """Health endpoint should exist."""
        response = client.get('/api/health')
        # May fail if DB not connected, but endpoint should exist
        assert response.status_code in [200, 500]
    
    def test_tables_endpoint_exists(self, client):
        """Tables endpoint should exist."""
        response = client.get('/api/tables')
        assert response.status_code in [200, 500]
    
    def test_games_endpoint_exists(self, client):
        """Games endpoint should exist."""
        response = client.get('/api/games')
        assert response.status_code in [200, 500]
    
    def test_status_endpoint_exists(self, client):
        """Status endpoint should exist."""
        response = client.get('/api/status')
        assert response.status_code in [200, 500]


class TestAPIResponseFormat:
    """Test API response format consistency."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.api.server import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_response_has_success_field(self, client):
        """All responses should have success field."""
        response = client.get('/api/health')
        data = response.get_json()
        assert 'success' in data
    
    def test_response_has_timestamp(self, client):
        """All responses should have timestamp."""
        response = client.get('/api/health')
        data = response.get_json()
        assert 'timestamp' in data
    
    def test_404_returns_json(self, client):
        """404 errors should return JSON."""
        response = client.get('/api/nonexistent')
        assert response.content_type == 'application/json'
        data = response.get_json()
        assert data['success'] is False


class TestAPITableEndpoint:
    """Test table data endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.api.server import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_tables_returns_list(self, client):
        """Tables endpoint should return a list."""
        response = client.get('/api/tables')
        if response.status_code == 200:
            data = response.get_json()
            assert 'data' in data
            assert 'tables' in data['data']
            assert isinstance(data['data']['tables'], list)
    
    def test_table_data_pagination(self, client):
        """Table data should support pagination params."""
        response = client.get('/api/tables/dim_player?limit=5&offset=0')
        if response.status_code == 200:
            data = response.get_json()
            assert 'limit' in data['data']
            assert 'offset' in data['data']
            assert data['data']['limit'] == 5


class TestAPIUploadEndpoint:
    """Test file upload endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.api.server import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_upload_requires_file(self, client):
        """Upload should reject requests without file."""
        response = client.post('/api/upload')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_upload_rejects_invalid_extension(self, client):
        """Upload should reject invalid file types."""
        from io import BytesIO
        data = {'file': (BytesIO(b'test'), 'test.txt')}
        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
