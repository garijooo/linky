import pytest
import json
from app import redis_store

class TestShortenLink:
    def test_ok(self, client):
        full_link = "https://example.com"
        init_data = {"fullLink": full_link}

        response = client.post("/shorten-link", json=init_data)
        data = json.loads(response.data.decode("utf-8"))
        short_link = data["short_link"].split("/")[-1]

        assert response.status_code == 200
        assert redis_store.get(short_link).decode("utf-8") == full_link


    def test_incomplete_link_ok(self, client):
        full_link = "example.com"
        init_data = {"fullLink": full_link}

        response = client.post("/shorten-link", json=init_data)
        data = json.loads(response.data.decode("utf-8"))
        short_link = data["short_link"].split("/")[-1]

        assert response.status_code == 200
        assert redis_store.get(short_link).decode("utf-8") == "http://" + full_link


    def test_duplicate_link_ok(self, client):
        redis_store.flushdb()
        full_link = "example.com"
        init_data = {"fullLink": full_link}

        response = client.post("/shorten-link", json=init_data)
        data = json.loads(response.data.decode("utf-8"))
        short_link_1 = data["short_link"].split("/")[-1]
        user_id_1 = data["user_id"]
        client.set_cookie(key="userId", value=user_id_1)

        response = client.post("/shorten-link", json=init_data)
        data = json.loads(response.data.decode("utf-8"))
        short_link_2 = data["short_link"].split("/")[-1]
        user_id_2 = data["user_id"]

        assert user_id_1 == user_id_2
        assert short_link_1 == short_link_2


    def test_no_link_fail(self, client):
        init_data = {"fullLink": ""}
        response = client.post("/shorten-link", json=init_data)
        data = json.loads(response.data.decode("utf-8"))

        assert "error" in data
        assert data["error"] == "The link was not provided"


    def test_wrong_link_fail(self, client):
        init_data = {"fullLink": "example"}
        response = client.post("/shorten-link", json=init_data)
        data = json.loads(response.data.decode("utf-8"))

        assert "error" in data
        assert data["error"] == "Please provide a valid link"


class TestDeleteLink:
    def test_ok(self, client):
        redis_store.flushdb()
        full_link = "example.com"
        init_data = {"fullLink": full_link}

        response = client.post("/shorten-link", json=init_data)
        data = json.loads(response.data.decode("utf-8"))
        short_link = data["short_link"].split("/")[-1]
        user_id = data["user_id"]
        client.set_cookie(key="userId", value=user_id)

        response = client.delete("/link/" + short_link)
        data = json.loads(response.data.decode("utf-8"))
        assert not "error" in data
        assert data["success"] is True


    def test_auth_error(self, client):
        redis_store.flushdb()
        full_link = "example.com"
        init_data = {"fullLink": full_link}

        response = client.post("/shorten-link", json=init_data)
        data = json.loads(response.data.decode("utf-8"))
        short_link = data["short_link"].split("/")[-1]

        response = client.delete("/link/" + short_link)
        data = json.loads(response.data.decode("utf-8"))
        assert "error" in data
        assert data["error"] == "Authorization error"


class TestRedirectToLink:
    def test_ok(self, client):
        full_link = "https://example.com"
        init_data = {"fullLink": full_link}

        response = client.post("/shorten-link", json=init_data)
        data = json.loads(response.data.decode("utf-8"))
        short_link = data["short_link"].split("/")[-1]

        response = client.get(f"/{short_link}")

        assert response.status_code == 302
        assert full_link in response.data.decode("utf-8")


    def test_page_not_page_found_redirect(self, client):
        short_link = "123456790"
        response = client.get(f"/{short_link}")

        assert response.status_code == 307
