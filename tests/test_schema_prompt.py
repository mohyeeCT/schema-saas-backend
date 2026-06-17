from typing import get_args

from models import SchemaType
from utils.schema_prompt import SCHEMA_GUIDANCE, build_schema_prompt


def test_guidance_exactly_matches_supported_schema_types():
    assert set(SCHEMA_GUIDANCE) == set(get_args(SchemaType))


def test_guidance_preserves_specialized_schema_fields():
    assert "servesCuisine" in SCHEMA_GUIDANCE["Restaurant"]
    assert "medicalSpecialty" in SCHEMA_GUIDANCE["MedicalBusiness"]
    assert "practice areas" in SCHEMA_GUIDANCE["LegalService"]
    assert "recipeIngredient" in SCHEMA_GUIDANCE["Recipe"]
    assert "SearchAction" in SCHEMA_GUIDANCE["WebSite"]
    assert "thumbnailUrl" in SCHEMA_GUIDANCE["VideoObject"]


def test_prompt_requires_schema_tags_and_no_fabrication():
    prompt = build_schema_prompt(
        url="https://example.com/service",
        schema_type="LocalBusiness",
        scraped_content={"target_page": "Phone: +1 555 000 1111"},
        serp_data="",
    )

    assert "Return ONLY the raw JSON object wrapped in <schema></schema> tags" in prompt
    assert "Do NOT fabricate" in prompt
    assert "https://example.com/service" in prompt
    assert "Phone: +1 555 000 1111" in prompt
