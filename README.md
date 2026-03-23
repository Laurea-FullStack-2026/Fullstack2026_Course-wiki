# Fullstack 2026 Course Wiki

This repository is the central wiki for Fullstack 2026 workshop materials.

It aggregates and normalizes documentation from five workshop repositories:

1. https://github.com/Laurea-FullStack-2026/Workshop01_Web-development-basics
2. https://github.com/Laurea-FullStack-2026/Workshop02_Nodejs_Solution
3. https://github.com/Laurea-FullStack-2026/Workshop03_Express_Solution
4. https://github.com/Laurea-FullStack-2026/Workshop04_Mongodb
5. https://github.com/Laurea-FullStack-2026/WS05_REST_API

## Navigation

- Workshop index: [workshops/index.md](workshops/index.md)
- Workshop 01: [workshops/ws01.md](workshops/ws01.md)
- Workshop 02: [workshops/ws02.md](workshops/ws02.md)
- Workshop 03: [workshops/ws03.md](workshops/ws03.md)
- Workshop 04: [workshops/ws04.md](workshops/ws04.md)
- Workshop 05: [workshops/ws05.md](workshops/ws05.md)

## Sync Automation

Wiki content is synchronized by GitHub Actions using [scripts/sync_wiki.py](scripts/sync_wiki.py).

- Workflow file: [.github/workflows/wiki-sync.yml](.github/workflows/wiki-sync.yml)
- Source repository list: [config/workshops.json](config/workshops.json)

### Trigger Options

1. Manual: GitHub Actions workflow dispatch
2. Scheduled: Weekdays at 18:00 UTC

### Sync Output

- Updated workshop pages in the [workshops](workshops) folder
- Updated [workshops/index.md](workshops/index.md)
- Run report in [sync-report.json](sync-report.json)

## Local Run

Run sync locally from repository root:

```bash
python scripts/sync_wiki.py
```

## Notes

- If a source repository is unavailable, existing wiki files remain and the status is recorded as error/partial in generated pages and report.
- Relative links in imported README content are rewritten to absolute GitHub links.
