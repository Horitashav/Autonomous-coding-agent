"""Integration tests for FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient

from agent.api.main import app

client = TestClient(app)


class TestHealthAndVisualizer:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "postgresql"

    def test_flow_graph_endpoint(self):
        payload = {
            "code": "def solve(nums):\n    if not nums:\n        return 0\n    return sum(nums)"
        }
        response = client.post("/api/flow-graph", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) >= 4


class TestAuthAndChatFlow:
    @pytest.fixture
    def authenticated_headers(self):
        """Create a unique user and return authorized bearer headers."""
        import uuid

        uid = uuid.uuid4().hex[:8]
        signup_payload = {
            "email": f"test_{uid}@example.com",
            "username": f"user_{uid}",
            "password": "production_password_123",
        }
        res = client.post("/api/auth/signup", json=signup_payload)
        assert res.status_code == 201
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_current_user_profile(self, authenticated_headers):
        res = client.get("/api/auth/me", headers=authenticated_headers)
        assert res.status_code == 200
        assert "email" in res.json()
        assert "username" in res.json()

    def test_chat_lifecycle(self, authenticated_headers):
        # 1. Create chat
        create_res = client.post(
            "/api/chats/",
            json={"name": "Test Agent Session"},
            headers=authenticated_headers,
        )
        assert create_res.status_code == 201
        chat_data = create_res.json()
        chat_id = chat_data["chat_id"]
        assert chat_data["name"] == "Test Agent Session"

        # 2. List chats
        list_res = client.get("/api/chats/", headers=authenticated_headers)
        assert list_res.status_code == 200
        assert any(c["chat_id"] == chat_id for c in list_res.json())

        # 3. Rename chat
        rename_res = client.put(
            f"/api/chats/{chat_id}/rename",
            json={"name": "Renamed Agent Session"},
            headers=authenticated_headers,
        )
        assert rename_res.status_code == 200
        assert rename_res.json()["name"] == "Renamed Agent Session"

        # 4. Fetch details
        detail_res = client.get(f"/api/chats/{chat_id}", headers=authenticated_headers)
        assert detail_res.status_code == 200
        assert detail_res.json()["chat_id"] == chat_id

        # 5. Delete chat
        del_res = client.delete(f"/api/chats/{chat_id}", headers=authenticated_headers)
        assert del_res.status_code == 204

        # 6. Verify deleted
        verify_res = client.get(f"/api/chats/{chat_id}", headers=authenticated_headers)
        assert verify_res.status_code == 404
