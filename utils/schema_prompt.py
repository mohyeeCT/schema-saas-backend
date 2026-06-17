SCHEMA_GUIDANCE = {
    "LocalBusiness": "name, url, telephone, address, openingHoursSpecification, geo, sameAs, areaServed, hasOfferCatalog",
    "Organization": "name, url, logo, contactPoint, sameAs, address, foundingDate, founder",
    "Product": "name, description, image, brand, offers, aggregateRating, review, sku, gtin",
    "Service": "name, provider, areaServed, serviceType, offers, description, url",
    "FAQPage": "mainEntity array of Question objects with acceptedAnswer Answer objects",
    "Article": "headline, author, publisher, datePublished, dateModified, image, mainEntityOfPage",
    "BreadcrumbList": "itemListElement array of ListItem objects for every URL path level",
    "WebSite": "name, url, potentialAction SearchAction when site search exists, publisher",
    "SoftwareApplication": "name, operatingSystem, applicationCategory, offers, featureList, screenshot, author",
}


def build_schema_prompt(
    url: str,
    schema_type: str,
    scraped_content: dict[str, str],
    serp_data: str,
) -> str:
    guidance = SCHEMA_GUIDANCE.get(
        schema_type,
        f"Include relevant schema.org properties for {schema_type}.",
    )
    scraped_block = "\n\n".join(
        f"=== {name.upper()} ===\n{content}"
        for name, content in scraped_content.items()
        if content
    )

    return f"""You are a senior technical SEO specialist building production-grade schema.org JSON-LD markup.

TARGET URL: {url}
SCHEMA TYPE: {schema_type}

SCRAPED CONTENT:
{scraped_block or "No scraped content was available."}

SERP DATA:
{serp_data or "No SERP data was requested or available."}

REQUIRED PROPERTIES TO POPULATE FOR {schema_type}:
{guidance}

EXTRACTION RULES:
1. Scan all scraped sections, including headers, footers, navigation, and contact details.
2. Extract phone numbers, addresses, emails, social URLs, services, staff names, reviews, and opening hours when present.
3. Use the most specific schema.org nested object types available.
4. Do NOT fabricate. Omit fields that are not supported by source content.
5. Prefer complete, deployable JSON-LD.

OUTPUT FORMAT: Return ONLY the raw JSON object wrapped in <schema></schema> tags. No explanation, no markdown fences.
"""
