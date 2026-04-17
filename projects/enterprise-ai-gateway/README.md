# Enterprise AI Gateway (Architecture/Cloud)

A reference implementation of an internal “secure AI portal” (similar to enterprise chat hubs) with:

- A lightweight web UI for employees
- A policy-enforced backend gateway (FastAPI)
- Pluggable model providers (local mock by default, AWS Bedrock supported)
- Audit logging hooks and basic redaction controls

## Goals

- Centralize access to multiple LLMs behind one controlled entrypoint
- Enforce governance: allowlisted models, input size limits, basic secret/PII redaction
- Make it portable across organizations by swapping providers and policies

## Quickstart (Local Mock Provider)

```bash
cd projects/enterprise-ai-gateway
docker compose up --build
```

- UI: http://localhost:8100
- API: http://localhost:8100/api/models
- Docs: http://localhost:8100/docs

## AWS Bedrock

Set environment variables:

- `AWS_REGION=us-east-1`
- Standard AWS credentials (SSO or env vars)

Then run:

```bash
docker compose up --build
```

## Security & governance notes

This project demonstrates patterns commonly used for internal AI portals:

- Model allowlists and per-model limits
- Centralized audit logs
- Secret redaction before requests leave the gateway

For production hardening, typical additions include:

- SSO (OIDC/SAML) + RBAC/ABAC
- VPC-only deployment with private connectivity to Bedrock
- SIEM export, immutable audit logs, retention policies
- Advanced DLP/PII detection and prompt-injection defenses

## White-label UI options (when you don’t want to build UI)

For a “ChatGPT internal” experience you can self-host and brand, many teams deploy:

- LibreChat or Open WebUI for the UI
- A gateway/proxy that translates an OpenAI-compatible API to Bedrock (or other providers)

If you need workflows/RAG tooling, Dify is a common choice, at the cost of more operational complexity.
