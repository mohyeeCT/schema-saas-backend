from unittest.mock import Mock, patch

import requests

from routers import schema
from utils.scraper import build_scrape_targets, scrape_with_firecrawl, scrape_with_jina


def test_build_scrape_targets_respects_toggles():
    targets = build_scrape_targets(
        "https://example.com/services/local",
        scrape_target=True,
        scrape_homepage=True,
        deep_scrape=True,
    )

    assert targets == [
        ("target_page", "https://example.com/services/local"),
        ("homepage", "https://example.com"),
        ("about", "https://example.com/about-us"),
        ("contact", "https://example.com/contact-us"),
    ]


@patch("utils.scraper.requests.get")
def test_scrape_with_jina_uses_reader_endpoint(mock_get):
    response = Mock(status_code=200, text="Example content")
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    content = scrape_with_jina("https://example.com", api_key="jina-secret")

    assert content == "Example content"
    assert mock_get.call_args.args[0] == "https://r.jina.ai/https://example.com"
    assert mock_get.call_args.kwargs["headers"]["Authorization"] == "Bearer jina-secret"
    assert mock_get.call_args.kwargs["headers"]["X-Timeout"] == "180"
    assert mock_get.call_args.kwargs["timeout"] == 200


@patch("utils.scraper.requests.get")
def test_scrape_with_jina_uses_cached_fallback_after_timeout(mock_get):
    cached = Mock(status_code=200, text="Cached page content")
    cached.raise_for_status.return_value = None
    mock_get.side_effect = [requests.exceptions.Timeout(), cached]

    content = scrape_with_jina("https://example.com", api_key="jina-secret")

    assert content == "Cached page content"
    assert mock_get.call_count == 2
    fallback = mock_get.call_args_list[1]
    assert fallback.kwargs["timeout"] == 30
    assert fallback.kwargs["headers"]["Authorization"] == "Bearer jina-secret"
    assert "X-No-Cache" not in fallback.kwargs["headers"]
    assert "X-Remove-Selector" not in fallback.kwargs["headers"]
    assert "X-Timeout" not in fallback.kwargs["headers"]


@patch("utils.scraper.requests.post")
def test_scrape_with_firecrawl_uses_api_key(mock_post):
    response = Mock(status_code=200)
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "success": True,
        "data": {"markdown": "Firecrawl content"},
    }
    mock_post.return_value = response

    content = scrape_with_firecrawl("https://example.com", "fc-secret")

    assert content == "Firecrawl content"
    assert mock_post.call_args.args[0] == "https://api.firecrawl.dev/v2/scrape"
    assert mock_post.call_args.kwargs["headers"]["Authorization"] == "Bearer fc-secret"
    assert mock_post.call_args.kwargs["timeout"] == 135
    assert mock_post.call_args.kwargs["json"]["timeout"] == 120000
    assert mock_post.call_args.kwargs["json"]["maxAge"] == 0
    assert mock_post.call_args.kwargs["json"]["storeInCache"] is False


def test_schema_scraper_defaults_to_jina_without_using_firecrawl():
    with patch.object(schema, "scrape_with_jina", return_value="Jina content") as jina, \
         patch.object(schema, "scrape_with_firecrawl") as firecrawl:
        content = schema._scrape_source(
            "https://example.com",
            {
                "scrape_provider": "jina",
                "jina_api_key": "jina-secret",
                "firecrawl_api_key": "fc-secret",
                "firecrawl_fallback": False,
            },
        )

    assert content == "Jina content"
    jina.assert_called_once_with("https://example.com", api_key="jina-secret")
    firecrawl.assert_not_called()


def test_schema_scraper_uses_firecrawl_only_after_jina_failure_when_enabled():
    with patch.object(schema, "scrape_with_jina", side_effect=RuntimeError("Jina failed")), \
         patch.object(schema, "scrape_with_firecrawl", return_value="Firecrawl content") as firecrawl:
        content = schema._scrape_source(
            "https://example.com",
            {
                "scrape_provider": "jina",
                "jina_api_key": "jina-secret",
                "firecrawl_api_key": "fc-secret",
                "firecrawl_fallback": True,
            },
        )

    assert content == "Firecrawl content"
    firecrawl.assert_called_once_with("https://example.com", "fc-secret")


def test_schema_primary_firecrawl_skips_jina():
    with patch.object(schema, "scrape_with_jina") as jina, \
         patch.object(schema, "scrape_with_firecrawl", return_value="Firecrawl content") as firecrawl:
        content = schema._scrape_source(
            "https://example.com",
            {
                "scrape_provider": "firecrawl",
                "firecrawl_api_key": "fc-secret",
            },
        )

    assert content == "Firecrawl content"
    jina.assert_not_called()
    firecrawl.assert_called_once_with("https://example.com", "fc-secret")
