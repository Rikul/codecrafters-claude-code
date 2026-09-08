import json
from unittest.mock import MagicMock, patch

import httpx

from app.tools.hackernews import HackerNewsTool

hackernews = HackerNewsTool.call


def _http_error(url: str) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", url)
    response = httpx.Response(500, request=request)
    return httpx.HTTPStatusError("server error", request=request, response=response)


def test_hackernews_returns_story_json():
    topstories_response = MagicMock()
    topstories_response.raise_for_status.return_value = None
    topstories_response.json.return_value = [101, 202]

    story_one_response = MagicMock()
    story_one_response.raise_for_status.return_value = None
    story_one_response.json.return_value = {"id": 101, "title": "Story One", "by": "alice"}

    story_two_response = MagicMock()
    story_two_response.raise_for_status.return_value = None
    story_two_response.json.return_value = {"id": 202, "title": "Story Two"}

    client = MagicMock()
    client.get.side_effect = [topstories_response, story_one_response, story_two_response]

    with patch("app.tools.hackernews.httpx.Client") as mock_client_class:
        mock_client_class.return_value.__enter__.return_value = client

        result = hackernews(2)

    assert json.loads(result) == [
        {"id": 101, "title": "Story One", "by": "alice", "username": "alice"},
        {"id": 202, "title": "Story Two", "username": "unknown"},
    ]


def test_hackernews_returns_error_on_topstories_http_error():
    topstories_response = MagicMock()
    topstories_response.raise_for_status.side_effect = _http_error(
        "https://hacker-news.firebaseio.com/v0/topstories.json"
    )

    client = MagicMock()
    client.get.return_value = topstories_response

    with patch("app.tools.hackernews.httpx.Client") as mock_client_class:
        mock_client_class.return_value.__enter__.return_value = client

        result = hackernews(1)

    assert result.startswith("Error getting hackernews stories:")
    topstories_response.json.assert_not_called()


def test_hackernews_returns_error_on_story_http_error():
    topstories_response = MagicMock()
    topstories_response.raise_for_status.return_value = None
    topstories_response.json.return_value = [101]

    story_response = MagicMock()
    story_response.raise_for_status.side_effect = _http_error(
        "https://hacker-news.firebaseio.com/v0/item/101.json"
    )

    client = MagicMock()
    client.get.side_effect = [topstories_response, story_response]

    with patch("app.tools.hackernews.httpx.Client") as mock_client_class:
        mock_client_class.return_value.__enter__.return_value = client

        result = hackernews(1)

    assert result.startswith("Error getting hackernews stories:")
    story_response.json.assert_not_called()


def test_hackernews_uses_explicit_timeout():
    topstories_response = MagicMock()
    topstories_response.raise_for_status.return_value = None
    topstories_response.json.return_value = []

    client = MagicMock()
    client.get.return_value = topstories_response

    with patch("app.tools.hackernews.httpx.Client") as mock_client_class:
        mock_client_class.return_value.__enter__.return_value = client

        hackernews(0)

    timeout = mock_client_class.call_args.kwargs.get("timeout")
    assert timeout is not None
    assert timeout > 0
