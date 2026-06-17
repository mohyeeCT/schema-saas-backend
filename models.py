from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

SchemaType = Literal[
    "LocalBusiness",
    "Organization",
    "Product",
    "Service",
    "FAQPage",
    "Article",
    "BreadcrumbList",
    "WebSite",
    "SoftwareApplication",
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
    serp_check: bool = False
    dfs_login: str = ""
    include_script_tag: bool = True
    brand_profile_id: str = ""


class SchemaJobRequest(BaseModel):
    name: str = Field(default="Schema Generator Job", max_length=120)
    rows: list[SchemaRow] = Field(min_length=1, max_length=25)
    settings: SchemaSettings = Field(default_factory=SchemaSettings)
