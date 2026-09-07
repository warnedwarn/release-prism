# Release Prism

A promotion gate for release notes, signed test reports and security advisories. Each role is bound to a separate parsed HTTPS origin. Every fetched record must name the exact stored release version before consensus can begin. The nominated version is passed into both leader and validator prompts, and validators re-fetch all records and verify the exact PROMOTE, HOLD or INSUFFICIENT decision plus every stored check code.

Candidates can be assessed before their deadline or permissionlessly expired afterward. Duplicate IDs, source reuse, hostname ambiguity, forged digests, mismatched release evidence and invalid transitions are rejected. Full fetched bytes are hashed before the separately bounded model representation is created. Promotion logic lives in `promotion_engine/`; execute `python -m pytest gate_checks -q` for the release gate.

The control room includes a nomination-specific assessment countdown so operators can see when permissionless expiry becomes available.

The regression suite includes a candidate for `release-7` whose test report identifies `release-8`; the assessment is rejected and the candidate cannot enter `PROMOTED`.

## Verified deployment

- StudioNet contract: `0x72405f4dFC8D58061Da8ED7149Be64979d8c9D73`
- Reviewed source commit: `45890e6271b5f16ae1e5b5a9edc6f8edc2f7213f`
- The recorded network lifecycle nominates release `2.4.0`, stores three full-byte digests, and finishes in `PROMOTED`.
- Reproduce it with `python release_ops/smoke.py`; transaction hashes are stored under `evidence/`.
