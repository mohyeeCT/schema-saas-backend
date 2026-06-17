from unittest.mock import Mock, patch

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
    mock_get.return_value = Mock(ok=True, text="Example content")

    content = scrape_with_jina("https://example.com")

    assert content == "Example content"
    assert mock_get.call_args.args[0] == "https://r.jina.ai/https://example.com"


@patch("utils.scraper.requests.post")
def test_scrape_with_firecrawl_uses_api_key(mock_post):
    mock_post.return_value = Mock(
        ok=True,
        json=lambda: {"data": {"markdown": "Firecrawl content"}},
    )

    content = scrape_with_firecrawl("https://example.com", "fc-secret")

    assert content == "Firecrawl content"
    assert mock_post.call_args.kwargs["headers"]["Authorization"] == "Bearer fc-secret"
