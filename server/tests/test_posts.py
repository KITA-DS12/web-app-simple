import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_get_posts():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/posts")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_post():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/posts",
            json={"text": "Test post"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Test post"
    assert "id" in data