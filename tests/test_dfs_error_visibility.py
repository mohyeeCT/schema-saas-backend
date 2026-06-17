from unittest.mock import Mock, patch

import pytest
import requests

from utils import dfs


@patch("utils.dfs.requests.post", side_effect=requests.Timeout("request timed out"))
def test_serp_timeout_is_visible(mock_post):
    with pytest.raises(RuntimeError, match="DataForSEO request timed out"):
        dfs.get_serp_data("login", "password", "example.com")


@patch("utils.dfs.requests.post")
def test_serp_parses_items(mock_post):
    mock_post.return_value = Mock(
        ok=True,
        status_code=200,
        json=lambda: {
            "tasks": [{
                "status_code": 20000,
                "result": [{"items": [{"type": "organic", "title": "Example"}]}],
            }]
        },
    )

    result = dfs.get_serp_data("login", "password", "example.com")

    assert result[0]["title"] == "Example"
