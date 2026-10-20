import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.intent import (
    ShiftRequestMessageIntent,
    parse_shift_request_message_intent,
)


@pytest.mark.asyncio
async def test_accept_intent():
    mock_response = {
        "message": {"content": "ACCEPT"}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        result = await parse_shift_request_message_intent("yes I can take it")
        assert result == ShiftRequestMessageIntent.ACCEPT


@pytest.mark.asyncio
async def test_decline_intent():
    mock_response = {
        "message": {"content": "DECLINE"}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        result = await parse_shift_request_message_intent("nah I'm booked")
        assert result == ShiftRequestMessageIntent.DECLINE


@pytest.mark.asyncio
async def test_unknown_intent():
    mock_response = {
        "message": {"content": "UNKNOWN"}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        result = await parse_shift_request_message_intent("what time does it start?")
        assert result == ShiftRequestMessageIntent.UNKNOWN


@pytest.mark.asyncio
async def test_fallback_on_error():
    """If Ollama is down or returns an error, we should get UNKNOWN (not crash)."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectError("Connection refused")

        result = await parse_shift_request_message_intent("yes I can take it")
        assert result == ShiftRequestMessageIntent.UNKNOWN


@pytest.mark.asyncio
async def test_messy_accept():
    mock_response = {
        "message": {"content": "ACCEPT"}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        result = await parse_shift_request_message_intent("Yeah sure, put me down")
        assert result == ShiftRequestMessageIntent.ACCEPT