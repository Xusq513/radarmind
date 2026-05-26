## ADDED Requirements

### Requirement: Horizon entry splitting
The system SHALL split a Horizon daily summary entry into multiple Article objects by parsing the HTML content and separating each article with `<hr />` delimiters.

#### Scenario: Single entry with multiple articles
- **WHEN** a Horizon Atom entry contains content with `<hr />` separators between articles
- **THEN** the parser SHALL create one Article per section delimited by `<hr />`

#### Scenario: Entry with no hr separators
- **WHEN** a Horizon entry content contains no `<hr />` separator
- **THEN** the parser SHALL fall back to treating the entire entry content as a single Article

### Requirement: Article field extraction
The system SHALL extract from each article section:
- **link**: The href from the first `<a>` tag inside the `<h2>` element
- **title**: The text content of the `<h2>` element with rating suffix removed
- **description**: All `<p>` elements following the `<h2>` up to the next separator or end
- **pub_date**: The `published` date of the parent entry
- **source**: The configured source name for Horizon

#### Scenario: Article with star rating
- **WHEN** an article h2 text is "Some Title ⭐️ 9.0/10"
- **THEN** the extracted title SHALL be "Some Title" (rating removed)

#### Scenario: Article without rating
- **WHEN** an article h2 text is "Some Title"
- **THEN** the extracted title SHALL be "Some Title" (unchanged)

#### Scenario: Article body extraction
- **WHEN** article section contains multiple `<p>` elements followed by `<details>` and `<p><strong>Tags</strong>`
- **THEN** the description SHALL include all `<p>` elements but exclude tags section

### Requirement: Horizon factory integration
The system SHALL support `type: "horizon"` in `config.json` sources and route such sources to the horizon parser via factory.py.

#### Scenario: Horizon source in config
- **WHEN** config.json contains a source with `"type": "horizon"`
- **THEN** the factory SHALL create a HorizonParser instance for that source