import uuid

from app.config import settings


def _auth(client, email, admin_expected):
    pw = "supersecret1"
    r = client.post("/api/v1/auth/register", json={"email": email, "password": pw})
    assert r.status_code == 201
    assert r.json()["is_admin"] is admin_expected
    r = client.post("/api/v1/auth/login", data={"username": email, "password": pw})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200


def test_requires_auth(client):
    assert client.get("/api/v1/documents").status_code == 401
    assert client.post("/api/v1/query", json={"question": "hello?"}).status_code == 401


def test_end_to_end_upload_and_cited_answer(client, monkeypatch):
    monkeypatch.setattr(settings, "min_similarity", 0.0)
    admin = _auth(client, f"admin-{uuid.uuid4().hex[:6]}@example.com", True)
    user = _auth(client, f"user-{uuid.uuid4().hex[:6]}@example.com", False)

    files = {
        "file": (
            "leave-policy.txt",
            b"Casual leave: every employee receives 12 casual leaves per year.\n\n"
            b"Maternity leave: 26 weeks of paid maternity leave.",
            "text/plain",
        )
    }
    # non-admin cannot upload
    assert client.post("/api/v1/documents", files=files, headers=user).status_code == 403
    r = client.post("/api/v1/documents", files=files, headers=admin)
    assert r.status_code == 202
    doc_id = r.json()["id"]

    doc = client.get(f"/api/v1/documents/{doc_id}", headers=user).json()
    assert doc["status"] == "ready" and doc["num_chunks"] >= 1

    r = client.post(
        "/api/v1/query", json={"question": "How many casual leaves per year?"}, headers=user
    )
    assert r.status_code == 200
    body = r.json()
    assert body["sources"][0]["filename"] == "leave-policy.txt"
    assert body["sources"][0]["cited"] is True
    assert "12 casual leaves" in body["sources"][0]["snippet"]


def test_rejects_bad_file_type(client):
    admin = _auth(client, f"a2-{uuid.uuid4().hex[:6]}@example.com", False)  # not first user
    r = client.post(
        "/api/v1/documents",
        files={"file": ("x.exe", b"MZ", "application/octet-stream")},
        headers=admin,
    )
    assert r.status_code in (403, 415)
