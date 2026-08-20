# Security Policy

## Reporting a vulnerability

Please do not publish credential leaks, webhook bypasses, or other security-sensitive issues in a public issue. Instead, contact the maintainer through [Telegram](https://t.me/MengliyevBahrom) with a concise description, reproduction details, and potential impact.

Reports are reviewed privately. This repository’s security-related utilities are provided for educational and portfolio purposes and should be independently reviewed before use in a production environment.

## Safe handling expectations

Do not commit `.env` files, access tokens, private keys, or real webhook payloads. The repository CI includes credential-like pattern checks; a detected secret should be revoked and removed from Git history as soon as possible.
