# Release and Tag Strategy for Workshop Sync Milestones

This document defines how to version, tag, and release the course wiki after meaningful sync milestones.

## Goals

1. Make each important sync state reproducible.
2. Keep a clean history of what changed across workshops.
3. Provide a predictable rollback point when source repositories change unexpectedly.

## What Counts as a Milestone

Create a release/tag when at least one of these is true:

1. A workshop source repository is corrected or added.
2. Sync status improves for one or more workshops (for example error -> ok).
3. Automation behavior changes (workflow, sync script, token handling).
4. Wiki structure changes (templates, navigation, section model).
5. All workshops are in a desired status for a course checkpoint.

## Versioning Model

Use semantic versions for milestone releases:

- `vMAJOR.MINOR.PATCH`

Rules:

1. `MAJOR`: Breaking policy or structure changes in the wiki process.
2. `MINOR`: New workshop coverage, major sync improvements, or process additions.
3. `PATCH`: Small corrections, link fixes, and non-breaking automation tweaks.

## Tag Types

Use two tag families:

1. Milestone release tag (annotated): `vMAJOR.MINOR.PATCH`
2. Operational sync tag (annotated, optional between releases): `sync-YYYYMMDD-HHMM`

Examples:

- `v1.0.0` -> Initial working wiki automation baseline
- `v1.1.0` -> Workshop02 and Workshop03 source correction completed
- `v1.2.0` -> Token-based private repo access for Workshop05
- `sync-20260323-1817` -> Snapshot after a significant successful sync run

## Milestone Definitions for This Repository

Recommended initial milestones:

1. `v1.0.0`: First automated wiki scaffold and sync workflow established.
2. `v1.1.0`: Workshop02 + Workshop03 source link corrections validated.
3. `v1.2.0`: Private repository token access implemented for Workshop05.
4. `v1.3.0`: Workshop05 becomes public and all 5 workshops sync as `ok`.
5. `v1.4.0`: Quality gates added (markdown lint + link checks).

## Release Checklist

Before creating a release tag:

1. Run sync and confirm expected statuses in `workshops/index.md`.
2. Confirm `sync-report.json` is updated in the same commit.
3. Ensure `README.md` navigation links are valid.
4. Confirm no accidental secrets or credentials are committed.
5. Validate GitHub Actions workflow is passing.

## Release Notes Template

Use this structure for each GitHub Release:

1. Scope: what milestone this release represents.
2. Workshop status summary:
   - `ws01`: status
   - `ws02`: status
   - `ws03`: status
   - `ws04`: status
   - `ws05`: status
3. Automation changes.
4. Known limitations.
5. Next milestone target.

## Tag and Release Commands

Example local workflow:

```bash
git checkout main
git pull origin main
python scripts/sync_wiki.py
git add README.md config/ docs/ scripts/ workshops/ sync-report.json .github/workflows/
git commit -m "chore: milestone sync v1.2.0"
git push origin main

git tag -a v1.2.0 -m "Milestone v1.2.0: token-based private repo access for Workshop05"
git push origin v1.2.0
```

Then create a GitHub Release from tag `v1.2.0` using the release notes template.

## Rollback Strategy

If a sync introduces broken wiki output:

1. Revert to the last stable milestone tag.
2. Re-run sync in a branch and inspect diffs before re-merging.
3. If needed, create a hotfix patch release:
   - Example: `v1.2.1`

## Branch and Protection Guidance

1. Create milestone changes via pull requests.
2. Protect `main` with at least one review if team size allows.
3. Require workflow checks for merge when quality gates are added.

## Ownership

Define one release owner per milestone who is responsible for:

1. Running the release checklist.
2. Creating tag + GitHub Release.
3. Posting a short changelog update for instructors.
