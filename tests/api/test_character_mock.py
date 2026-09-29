"""Exercise real config, provider wiring, job envelope and pipeline without GPU."""

import asyncio
import base64
import os
import socket
import struct
import zlib

import httpx
import pytest

from api.config import AppConfig, MissingEnvError
from api.main import create_app


@pytest.fixture
def mock_env(monkeypatch):
    # Avoid developer .env credentials/providers leaking into this offline check.
    for key in list(os.environ):
        if key.startswith(("RUNPOD_", "QWEN_", "PLANNER_OPENAI_", "AWS_", "LANGSMITH_")):
            monkeypatch.delenv(key)
    monkeypatch.delenv("LORA_DIR", raising=False)
    monkeypatch.setenv("MONGLE_API_KEY", "mock-test-key")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("QUEST_LLM_PROVIDER", "fake")
    monkeypatch.setenv("FEED_LLM_PROVIDER", "fake")
    monkeypatch.setenv("IMAGE_PROVIDER", "mock")
    monkeypatch.setenv("STORAGE_BACKEND", "local")

    def deny_network(*args, **kwargs):
        raise AssertionError("Mock character flow must not open network sockets")

    monkeypatch.setattr(socket.socket, "connect", deny_network)


def test_mock_keeps_auth_and_storage_requirements(mock_env, monkeypatch):
    cfg = AppConfig.from_env()
    assert cfg.runpod_image_endpoint_url is None
    assert cfg.runpod_character_endpoint_url is None
    assert cfg.lora_dir == ""
    monkeypatch.delenv("MONGLE_API_KEY")
    with pytest.raises(MissingEnvError, match="MONGLE_API_KEY"):
        AppConfig.from_env()
    monkeypatch.setenv("MONGLE_API_KEY", "mock-test-key")
    monkeypatch.setenv("STORAGE_BACKEND", "s3")
    with pytest.raises(MissingEnvError, match="AWS_S3_BUCKET.*AWS_REGION"):
        AppConfig.from_env()


async def test_mock_character_real_lifespan_and_job_flow(mock_env):
    app = create_app()
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            body = {"user_id": "mock-user", "name": "진단", "persona": "차분한 친구"}
            assert (await client.post("/v1/character", json=body)).status_code == 401
            headers = {"X-API-Key": "mock-test-key"}
            assert (await client.get("/v1/character/missing", headers=headers)).status_code == 404
            assert (await client.post("/v1/character", json={}, headers=headers)).status_code == 422
            assert (await client.post("/v1/character/warmup", headers=headers)).status_code == 202
            submitted = await client.post("/v1/character", json=body, headers=headers)
            assert submitted.status_code == 202
            envelope = submitted.json()
            assert envelope["status"] == "pending"
            job_id = envelope["result"]["job_id"]
            for _ in range(200):
                await asyncio.sleep(0.01)
                result = (await client.get(f"/v1/character/{job_id}", headers=headers)).json()
                if result["status"] != "pending":
                    break
            assert result["status"] == "done", result
            entity = result["result"]
            assert entity["name"] == body["name"]
            assert entity["appearance"]
            assert entity["source_image_url"] is None
            png = base64.b64decode(entity["image_url"].split(",", 1)[1])
            assert png[:8] == b"\x89PNG\r\n\x1a\n"
            offset = 8
            image_data = b""
            while offset < len(png):
                length = struct.unpack(">I", png[offset:offset + 4])[0]
                kind = png[offset + 4:offset + 8]
                data = png[offset + 8:offset + 8 + length]
                crc = struct.unpack(">I", png[offset + 8 + length:offset + 12 + length])[0]
                assert crc == zlib.crc32(kind + data)
                if kind == b"IHDR":
                    assert struct.unpack(">II", data[:8]) == (64, 64)
                if kind == b"IDAT":
                    image_data += data
                offset += 12 + length
            assert len(zlib.decompress(image_data)) == 64 * (1 + 64 * 3)
