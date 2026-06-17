from utils.schema_prompt import SCHEMA_GUIDANCE, build_schema_prompt


def test_guidance_contains_initial_supported_schema_types():
    expected = {
        "LocalBusiness",
        "Organization",
        "Product",
        "Service",
        "FAQPage",
        "Article",
        "BreadcrumbList",
        "WebSite",
        "SoftwareApplication",
    }

    assert expected.issubset(set(SCHEMA_GUIDANCE))


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
