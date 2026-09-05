# Release Prism

A promotion gate for release notes, signed test reports and security advisories. Each role is bound to a separate HTTPS origin. Validators re-fetch all records and verify the exact PROMOTE, HOLD or INSUFFICIENT decision plus every stored check code.

Candidates can be assessed before their deadline or permissionlessly expired afterward. Duplicate IDs, source reuse, forged digests and invalid transitions are rejected. Promotion logic lives in `promotion_engine/`; execute `python -m pytest gate_checks -q` for the release gate.
