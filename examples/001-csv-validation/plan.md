# Plan: reject malformed CSV before import
## Source
[intent.md](intent.md), [spec.md](spec.md). Illustrative draft; no approval evidence.
## Approach
Parse and validate bounded input completely before calling the existing writer.
## Affected components
Importer and its tests; actual file paths must be discovered in the target repository.
## Implementation steps
1. Find import entry point, parser behavior, fixtures and writer abstraction.
2. Add tests for AC-01 through AC-06 and demonstrate the current failure where applicable.
3. Add validation before writes; preserve valid-path behavior.
4. Run focused tests and the existing regression suite.
## Verification
| Criterion | Check | Expected result | Environment |
| --- | --- | --- | --- |
| AC-01 | Missing-header fixtures, writer spy | Error, zero writes | Unit tests |
| AC-02 | Empty SKU and invalid quantity table | Row/field error, zero writes | Unit tests |
| AC-03 | Existing valid-file fixtures | Unchanged outcomes | Existing suite |
| AC-04 | Valid first row, invalid later row | Error, zero writes | Unit tests |
| AC-05 | Header-only file | Success, zero writes | Unit tests |
| AC-06 | Parser-error fixture | Error, zero writes | Unit tests |
Exact test commands depend on the target repository and are not yet established.
## Risks
Parser permissiveness may hide malformed input. Test actual parser behavior. Full input
buffering assumes bounded files; reject that assumption if the real workload is larger.
## Deviations
None. No implementation or execution evidence is claimed.
