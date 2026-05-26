## ADDED Requirements

### Requirement: Title extraction from h2
The system SHALL extract the article title from the text content of an `<h2 id="item-N">` element within a Horizon article section.

#### Scenario: Title with star rating
- **WHEN** h2 text is "Spyware Backdoor Found in Telegram on APKPure ⭐️ 9.0/10"
- **THEN** the extracted title SHALL be "Spyware Backdoor Found in Telegram on APKPure"

#### Scenario: Title without rating
- **WHEN** h2 text is "Some Article Title"
- **THEN** the extracted title SHALL be "Some Article Title"

### Requirement: Link extraction from h2
The system SHALL extract the href attribute from the first `<a>` tag inside an `<h2>` element as the article link.

#### Scenario: Link in first anchor
- **WHEN** h2 contains `<a href="https://example.com">Title</a> ⭐️ 8.0/10`
- **THEN** the extracted link SHALL be "https://example.com"

#### Scenario: Multiple anchors in h2
- **WHEN** h2 contains multiple `<a>` tags (e.g., main link + discussion link)
- **THEN** only the first anchor's href SHALL be used

### Requirement: Rating suffix removal
The system SHALL remove rating suffix patterns from title text using the pattern ` ⭐️ \d+\.\d+/10$`.

#### Scenario: Rating pattern variation
- **WHEN** title text matches ` ⭐️ X.X/10` pattern where X is digit
- **THEN** the system SHALL strip the matching suffix