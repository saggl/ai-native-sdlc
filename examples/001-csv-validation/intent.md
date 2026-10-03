# Intent: reject malformed CSV before import
## Metadata
Illustrative draft only; no human approval or implemented code.
## Problem
A local inventory import can begin writing records before discovering a missing SKU.
## Desired outcome
Reject malformed input before any inventory records are written.
## Scope
Included: required sku and quantity columns, nonempty SKU and nonnegative integer quantity.
Excluded: duplicate resolution changes, streaming huge files and new storage backends.
## Constraints
Preserve the existing valid-file behavior and duplicate handling.
## Success
All invalid fixtures produce no inventory writes and a useful row/field error.
## Open questions
None for this fictional example. Verify assumptions in a real repository.
