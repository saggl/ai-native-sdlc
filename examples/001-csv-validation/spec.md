# Specification: reject malformed CSV before import
## Source
[intent.md](intent.md), illustrative draft, not approved.
## Required behavior
Validate the entire input before invoking the existing write path. Header-only input is
valid with zero writes. Data rows are numbered from 2, since the header is row 1.
## Interfaces and data
Keep the existing import entry point and duplicate behavior. Require sku and quantity
headers. SKU is nonempty after trimming. Quantity is a base-10 digit string with optional
surrounding whitespace; no sign, decimal or exponent. Additional columns remain allowed.
## Failure cases and boundaries
Missing headers, malformed CSV and invalid required fields fail without writes. Report
header/parse errors clearly; row validation errors include row and field.
## Quality requirements
No additional network calls; assume bounded local files for this example.
## Acceptance criteria
- AC-01: Missing required headers fail before writes.
- AC-02: Empty SKU or invalid quantity reports row/field and produces zero writes.
- AC-03: Existing valid fixtures retain their import outcomes.
- AC-04: A valid row followed by an invalid row produces zero writes.
- AC-05: Header-only input produces zero writes without error.
- AC-06: Malformed CSV produces an error before writes.
## Open questions
None for this illustrative draft.
