# Security Policy

## Supported versions

`v0.5.x` receives security and release-packaging fixes while this project is actively maintained.

## Reporting a vulnerability

Please do not publish real credentials, private student information, downloaded copyrighted exam files, or exploit details in public issues. Use GitHub Security Advisories when available, or contact the maintainer through the GitHub profile linked from the repository.

Include:

- affected script, provider, or workflow
- reproduction steps
- expected impact
- whether student data, private files, or provider credentials were involved

## Sensitive data and copyrighted material

Do not commit:

- API keys or provider credentials
- generated student-specific handbooks with private data
- downloaded official PDFs, past papers, mark schemes, textbook pages, or paid resources unless redistribution rights are explicit
- browser traces or screenshots containing private student information

## Source and provider boundary

Official exam-board materials remain owned by their respective rights holders. New code paths that fetch, parse, or render source material must preserve the copyright and non-affiliation boundaries described in `DISCLAIMER.md`.
