# Contributing Guidelines

Thank you for your interest! To preserve the integrity of the timekeeping definition, the Core is FROZEN.

## What You May Contribute
- Bug reports / algorithmic correctness issues (with evidence, references).
- Performance optimizations that do NOT alter externally observable results.
- Extensions (new modules outside `src/astronomical_watch/core/`).
- Tooling: CLI improvements, packaging, docs, integration layers, web banner widgets.

## What Will Be Rejected
- Fundamental spec changes without a compelling astronomical justification.
- API-breaking changes within the Core.
- Modified redistributions of Core files (except temporary Security Exception patches per LICENSE.CORE §11).

## Process
1. Open an issue describing intent.
2. For code changes, fork and open a PR (Core changes limited to bug fixes maintaining invariant behavior).
3. Include tests. New features outside Core must have accompanying tests.

## License Notes
- Core: Astronomical Watch Core License v1.0 (no modification redistribution; security exception for urgent fixes).
- Non-core: MIT (see LICENSE.MIT).

By submitting a contribution you agree that the project maintainer may relicense your contribution under future dual-license terms consistent with the project's goals.
