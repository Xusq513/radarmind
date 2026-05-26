## 1. Horizon Parser Implementation

- [x] 1.1 Create `src/radar_mind/sources/horizon.py` with `parse_horizon()` function
- [x] 1.2 Implement `split_by_hr()` to split HTML content by `<hr />` delimiter
- [x] 1.3 Implement `extract_title_from_h2()` to extract title and strip rating suffix
- [x] 1.4 Implement `extract_link_from_h2()` to get href from first anchor in h2
- [x] 1.5 Implement `extract_body_from_segment()` to extract article body paragraphs
- [x] 1.6 Add fallback for entries with no `<hr />` separators

## 2. Factory Integration

- [x] 2.1 Add `type: "horizon"` case in `sources/factory.py` create_parser()
- [x] 2.2 Update `config.json` Horizon source type from `"atom"` to `"horizon"`

## 3. Testing

- [x] 3.1 Add unit tests for `split_by_hr()` edge cases
- [x] 3.2 Add unit tests for title extraction with/without rating suffix
- [x] 3.3 Add unit tests for link extraction from h2
- [x] 3.4 Run existing tests to ensure no regression