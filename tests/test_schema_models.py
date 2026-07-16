from typing import get_args

import pytest
from pydantic import ValidationError

from models import SchemaJobRequest, SchemaRow, SchemaSettings, SchemaType


SCHEMA_TYPES = [
    "LocalBusiness",
    "Restaurant",
    "MedicalBusiness",
    "Dentist",
    "LegalService",
    "HomeAndConstructionBusiness",
    "FinancialService",
    "Store",
    "LodgingBusiness",
    "AutoDealer",
    "RealEstateAgent",
    "BeautySalon",
    "FitnessCenter",
    "Organization",
    "Corporation",
    "EducationalOrganization",
    "NonProfit",
    "FAQPage",
    "Article",
    "BlogPosting",
    "HowTo",
    "Recipe",
    "NewsArticle",
    "Product",
    "ItemList",
    "Person",
    "Event",
    "Service",
    "WebSite",
    "BreadcrumbList",
    "SoftwareApplication",
    "VideoObject",
]


def test_schema_type_catalog_exactly_matches_expected_values():
    assert set(get_args(SchemaType)) == set(SCHEMA_TYPES)


@pytest.mark.parametrize("schema_type", SCHEMA_TYPES)
def test_schema_settings_accepts_every_supported_schema_type(schema_type):
    settings = SchemaSettings(schema_type=schema_type)

    assert settings.schema_type == schema_type


def test_schema_settings_rejects_unknown_schema_type():
    with pytest.raises(ValidationError):
        SchemaSettings(schema_type="ImaginarySchema")


def test_schema_settings_defaults_are_safe():
    settings = SchemaSettings()

    assert settings.provider == "Claude"
    assert settings.schema_type == "LocalBusiness"
    assert settings.scrape_target is True
    assert settings.scrape_provider == "jina"
    assert settings.firecrawl_fallback is False
    assert settings.deep_scrape is False
    assert settings.serp_check is False


def test_schema_row_requires_http_url():
    row = SchemaRow(url="https://example.com/service")

    assert str(row.url) == "https://example.com/service"

    with pytest.raises(ValidationError):
        SchemaRow(url="not-a-url")


def test_schema_request_allows_single_row_mvp():
    request = SchemaJobRequest(
        name="Schema test",
        rows=[{"url": "https://example.com"}],
        settings={"schema_type": "Organization"},
    )

    assert request.name == "Schema test"
    assert request.settings.schema_type == "Organization"
    assert len(request.rows) == 1
