from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

SchemaType = Literal[
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


class SchemaRow(BaseModel):
    url: HttpUrl
    keyword: str = ""


class SchemaSettings(BaseModel):
    provider: str = "Claude"
    model: str = ""
    schema_type: SchemaType = "LocalBusiness"
    scrape_target: bool = True
    scrape_homepage: bool = True
    deep_scrape: bool = False
    scrape_provider: Literal["jina", "firecrawl"] = "jina"
    firecrawl_fallback: bool = False
    serp_check: bool = False
    dfs_login: str = ""
    include_script_tag: bool = True
    brand_profile_id: str = ""


class SchemaJobRequest(BaseModel):
    name: str = Field(default="Schema Generator Job", max_length=120)
    rows: list[SchemaRow] = Field(min_length=1, max_length=25)
    settings: SchemaSettings = Field(default_factory=SchemaSettings)
