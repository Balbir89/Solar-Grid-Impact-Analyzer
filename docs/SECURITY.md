# Credential handling

The earlier weather notebook contained a hard-coded API credential and saved request output. The rebuilt default branch candidate removes that notebook and needs no external API, account or secret.

**Repository owner action:** revoke or rotate the old credential with its provider. Removing a file does not revoke a credential or remove it from Git history, forks or existing clones. This change does not claim that rotation has happened.

Do not put replacement keys in source, notebook outputs, request URLs in logs, screenshots or committed environment files. If a future authenticated ingestion service is added, use environment variables locally and repository secrets for CI. Commit example variable names only.

The container serves only the generated public dashboard, runs as UID 10001, and does not serve the repository or its history. It is a portfolio web server; use a hardened web server/CDN, TLS and deployment monitoring for a real public production service.
