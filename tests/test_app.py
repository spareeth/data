import os
from types import SimpleNamespace

import pytest

import app as chatbot_app


@pytest.fixture()
def client(monkeypatch):
    """Flask test client with isolated session storage."""
    chatbot_app.app.config["TESTING"] = True
    with chatbot_app.app.test_client() as client:
        with client.session_transaction() as sess:
            sess.clear()
        yield client


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CSV-grounded Chatbot" in response.data


def test_chat_without_api_key_shows_notice(client, monkeypatch):
    # Ensure no API key is present and the OpenAI client is reset accordingly
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chatbot_app.client.api_key = None

    response = client.post("/chat", data={"message": "Hello"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"OpenAI API key is missing" in response.data


class _FakeCompletionChoice:
    def __init__(self, content: str):
        self.message = SimpleNamespace(content=content)


class _FakeCompletion:
    def __init__(self, content: str):
        self.choices = [_FakeCompletionChoice(content)]


class _FakeCompletions:
    def __init__(self, content: str):
        self._content = content

    def create(self, **_kwargs):
        return _FakeCompletion(self._content)


class _FakeChat:
    def __init__(self, content: str):
        self.completions = _FakeCompletions(content)


class _FakeOpenAIClient:
    def __init__(self, api_key: str, reply: str):
        self.api_key = api_key
        self.chat = _FakeChat(reply)


def test_chat_with_api_key_uses_openai_response(client, monkeypatch):
    fake_reply = "Here is a catalog-based response."
    fake_client = _FakeOpenAIClient(api_key="test-key", reply=fake_reply)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    chatbot_app.client = fake_client

    response = client.post("/chat", data={"message": "Any backpacks?"}, follow_redirects=True)
    assert response.status_code == 200
    assert fake_reply.encode() in response.data
