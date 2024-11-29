import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import redis
import uuid
from src.api import app, redis_client

@pytest.fixture(autouse=True)  # autouse=True makes the fixture automatically used by all test functions

def mock_redis_client():
    with patch('src.api.redis_client.get') as mock_get:
        # You can set a default return value here, or customize it in each test
        mock_get.return_value = "False"  # Default to maintenance mode off
        yield mock_get

# To avoid `@patch('src.api.redis_client.ping')` in every test, we can use a fixture to mock the ping method
# and return a value of True
@pytest.fixture
def mock_ping():
    with patch('src.api.redis_client.ping') as mock:
        mock.return_value = True
        yield mock

# To avois `@patch('src.api.client.chat.completions.create')` in every test, we can use a fixture to mock the
# completions.create method and return a value of "healthy"
@pytest.fixture
def mock_create():
    with patch('src.api.client.chat.completions.create') as mock:
        mock.return_value.choices[0].message.content = "healthy"
        yield mock

# Fixture for TestClient
@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

# Fixture for mocking uuid4
@pytest.fixture
def mock_uuid4():
    with patch('uuid.uuid4') as mock:
        mock.return_value = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        yield mock

@pytest.fixture
def mock_verify_jwt():
    with patch('api.verify_jwt') as mock:
        mock.return_value = {
            "aud": "892541",
            "jti": "4b55fd8c72f166859e21a459a521f72ea7289b6c454bcf53dfcac91fca2097c402bafa822db7db28",
            "iat": 1708119598,
            "nbf": 1708119598,
            "exp": 1708120498,
            "sub": "8051222",
            "scopes": []
        }
        yield mock


# Grouping health check tests into a class
class TestHealthCheck:
    def test_root(self, test_client):
        response = test_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"name": "My Assistant", "documentation": "/docs"}

    def test_health_check_server(self, test_client):
        response = test_client.get('/health-check/server')
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_health_check_datastore_healthy(self, mock_ping, test_client):
        response = test_client.get("/health-check/datastore")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        mock_ping.assert_called_once()

    def test_health_check_datastore_unhealthy(self, mock_ping, test_client):
        mock_ping.side_effect = redis.RedisError
        response = test_client.get("/health-check/datastore")
        assert response.status_code == 500
        mock_ping.assert_called_once()

    @patch('src.api.client.chat.completions.create')
    def test_health_check_model_healthy(self, mock_create, test_client):
        mock_create.return_value.choices[0].message.content = "healthy"
        response = test_client.get("/health-check/model")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        mock_create.assert_called_once()

    @patch('src.api.client.chat.completions.create')
    def test_health_check_model_unhealthy(self, mock_create, test_client):
        mock_create.return_value.choices[0].message.content = "unhealthy"
        response = test_client.get("/health-check/model")
        assert response.status_code == 500
        mock_create.assert_called_once()

    @patch('src.api.client.chat.completions.create')
    def test_health_check_model_error(self, mock_create, test_client):
        mock_create.side_effect = Exception
        response = test_client.get("/health-check/model")
        assert response.status_code == 500
        mock_create.assert_called_once()

# # Testing command execution with mocked UUID
# def test_command_execute(test_client, mock_uuid4, mock_verify_jwt):
#     test_client.headers = {"Authorization": f"Bearer {mock_verify_jwt.return_value}"}
#     response = test_client.post("/command/execute", json={"command": "test"})
#     assert response.status_code == 200
#     assert response.json() == {"id": "123e4567-e89b-12d3-a456-426614174000", "tl_id": "test", "command": "test", "response": "test"}
#     mock_uuid4.assert_called_once()

