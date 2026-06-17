SCHEMA_GUIDANCE = {
    "LocalBusiness": """REQUIRED FIELDS - populate every one that has a real data source:
- name (exact legal/brand name)
- alternateName (trading name or abbreviation if different)
- url (canonical homepage URL)
- telephone (E.164 format e.g. +12535722949)
- faxNumber (if found)
- email (if found)
- description (2-3 sentence business description)
- image (array of image URLs found on site)
- logo (logo image URL)
- priceRange (e.g. $$)
- address - use PostalAddress with: streetAddress, addressLocality, addressRegion, postalCode, addressCountry. If multiple locations found, use the PRIMARY/HQ address here and add a location[] array for all offices.
- location[] - array of Place objects each with name and full PostalAddress, for EVERY physical location found
- geo - GeoCoordinates with latitude and longitude if found
- openingHoursSpecification - array of OpeningHoursSpecification objects with dayOfWeek (array), opens (HH:MM), closes (HH:MM). Map "Mon-Fri" to individual day strings.
- areaServed - array of City or State objects for every service area mentioned
- sameAs - array of ALL confirmed external profile URLs: Facebook, LinkedIn, Instagram, Twitter/X, YouTube, Yelp, Google Maps, Crunchbase, ZoomInfo, BBB, Houzz, Angi, etc.
- hasOfferCatalog - OfferCatalog with itemListElement array. For EACH service/product found: create an Offer containing a Service or Product with name, description, url.
- knowsAbout - array of strings listing all specialties, industries served, or topic areas mentioned
- contactPoint - ContactPoint with telephone, contactType, areaServed, availableLanguage
- aggregateRating - if any review counts or star ratings found: ratingValue, reviewCount, bestRating
- foundingDate - if year founded is mentioned
- employee - array of Person objects for any named staff/team members found, each with name, jobTitle, image if available
- slogan - if a tagline is present
- currenciesAccepted, paymentAccepted - if mentioned""",
    "Restaurant": "All LocalBusiness fields plus: servesCuisine (array), menu (URL), hasMenu (URL), acceptsReservations (true/false), servesCuisine, aggregateRating (ratingValue, reviewCount), starRating",
    "MedicalBusiness": "All LocalBusiness fields plus: medicalSpecialty (array of specialties), availableService (array of MedicalTherapy or MedicalProcedure objects with name + description), employee (array of physicians with name, jobTitle, medicalSpecialty)",
    "Dentist": "All LocalBusiness fields plus: medicalSpecialty: Dentistry, availableService (array of dental services each with name + description + url), employee (dentists with name, jobTitle, image)",
    "LegalService": "All LocalBusiness fields plus: knowsAbout (all practice areas as array), hasOfferCatalog (all legal services), employee (attorneys with name, jobTitle, sameAs LinkedIn)",
    "HomeAndConstructionBusiness": "All LocalBusiness fields plus: areaServed (every city/county/state served), hasOfferCatalog (every service with name + description + url), knowsAbout (trade specialties)",
    "FinancialService": "All LocalBusiness fields plus: feesAndCommissionsSpecification, hasOfferCatalog (all financial products/services), knowsAbout (financial specialties)",
    "Store": "All LocalBusiness fields plus: currenciesAccepted, paymentAccepted, hasMap, openingHoursSpecification (full week), hasOfferCatalog (product categories)",
    "LodgingBusiness": "All LocalBusiness fields plus: amenityFeature (array of LocationFeatureSpecification with name+value), checkinTime, checkoutTime, starRating, numberOfRooms, petsAllowed, hasMap",
    "AutoDealer": "All LocalBusiness fields plus: brand (array of car brands sold), hasOfferCatalog (vehicle categories/services)",
    "RealEstateAgent": "All LocalBusiness fields plus: areaServed (every city/neighborhood served), knowsAbout (property types, buyer/seller services), hasOfferCatalog",
    "BeautySalon": "All LocalBusiness fields plus: hasOfferCatalog (every service with name + description + url), openingHoursSpecification, employee (stylists if named)",
    "FitnessCenter": "All LocalBusiness fields plus: amenityFeature (equipment/facilities), hasOfferCatalog (classes/memberships), openingHoursSpecification",
    "Organization": "name, alternateName, url, description, logo, image (array), email, telephone, faxNumber, address (PostalAddress), sameAs (ALL profiles), foundingDate, foundingLocation, numberOfEmployees, legalName, contactPoint (array), member (key members as Person), knowsAbout, areaServed, slogan",
    "Corporation": "All Organization fields plus: tickerSymbol, foundingLocation, numberOfEmployees, parentOrganization, subOrganization",
    "EducationalOrganization": "All Organization fields plus: hasCredential (array), alumni, department (array), hasOfferCatalog (programs/courses)",
    "NonProfit": "All Organization fields plus: nonprofitStatus, foundingDate, areaServed, hasOfferCatalog (programs), knowsAbout",
    "FAQPage": 'mainEntity: array of Question objects. For EVERY question-answer pair found on the page: { "@type": "Question", "name": "exact question text", "acceptedAnswer": { "@type": "Answer", "text": "complete answer text - include the full answer, do not truncate" } }. Extract ALL FAQ items, not just a few.',
    "Article": "headline, url, datePublished (ISO 8601), dateModified (ISO 8601), author (Person with name, url, sameAs), publisher (Organization with name, logo as ImageObject with url), image (ImageObject with url, width, height), description, articleBody (first 200 words), wordCount, articleSection, keywords (array), inLanguage",
    "BlogPosting": "headline, url, datePublished, dateModified, author (Person with name + url), publisher (Organization with name + logo ImageObject), image, description, keywords (array), articleSection",
    "HowTo": "name, description, image, totalTime (ISO 8601 PT format e.g. PT30M), estimatedCost (MonetaryAmount with currency + value), supply (array of HowToSupply with name), tool (array of HowToTool with name), step (array of HowToStep with @type, name, text, image - use ALL steps found on page)",
    "Recipe": "name, image (array), author (Person), datePublished, description, prepTime (PT), cookTime (PT), totalTime (PT), recipeCategory, recipeCuisine, recipeYield, nutrition (NutritionInformation), recipeIngredient (array - every ingredient), recipeInstructions (array of HowToStep with name + text), keywords",
    "NewsArticle": "headline, url, datePublished, dateModified, author (Person with name+url), publisher (NewsMediaOrganization with name+logo ImageObject), image (ImageObject), description, articleSection, keywords (array), dateline, inLanguage",
    "Product": "name, description, image (array), brand (Brand with name), sku, gtin13 or mpn, offers (Offer: price, priceCurrency, availability as schema.org URL, url, seller, priceValidUntil), aggregateRating (ratingValue, reviewCount), review (array of Review), category",
    "ItemList": "name, description, numberOfItems, itemListElement (array of ListItem: position, name, url, item with @type+name+url)",
    "Person": "name, alternateName, url, jobTitle, worksFor (Organization with name+url), email, telephone, image, description, address (PostalAddress), alumniOf (array of EducationalOrganization with name+description), knowsAbout (array of strings), memberOf (array of Organizations), sameAs (array: LinkedIn, Twitter, personal site, etc.), honorificPrefix",
    "Event": "name, startDate (ISO 8601), endDate (ISO 8601), eventStatus (EventScheduled etc), eventAttendanceMode, location (Place with name+address OR VirtualLocation with url), description, image, url, organizer (Organization/Person), performer (array), offers (Offer with price+url), typicalAgeRange",
    "Service": "name, description, url, provider (Organization with name+url+address+telephone), serviceType, category, areaServed (array), offers (Offer with price if available), availableChannel (ServiceChannel with serviceUrl+servicePhone), hasOfferCatalog (sub-services), isRelatedTo (array of related services), knowsAbout",
    "WebSite": 'name, url, description, inLanguage, sameAs (array), potentialAction (SearchAction: target EntryPoint with urlTemplate containing {search_term_string}, query-input: "required name=search_term_string"), publisher (Organization)',
    "BreadcrumbList": 'itemListElement: array of BreadcrumbItem for EVERY level of the page path. Each: { "@type": "ListItem", "position": N, "name": "Page Name", "item": "https://full-url" }. Derive from the page URL path and navigation found.',
    "SoftwareApplication": "name, operatingSystem (array), applicationCategory, offers (Offer with price), aggregateRating, downloadUrl, screenshot (array of ImageObject), featureList (array), softwareVersion, description, url, author (Organization)",
    "VideoObject": "name, description, thumbnailUrl, uploadDate (ISO 8601), duration (ISO 8601 PT), contentUrl, embedUrl, publisher (Organization with name+logo), interactionStatistic (InteractionCounter: userInteractionType WatchAction + userInteractionCount), keywords",
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
