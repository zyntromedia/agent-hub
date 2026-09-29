Next Improvements — FIG ZyntroAI CrystalCastle v1.7.0-MERGED-FIG → v1.8.0
Current State Analysis (v1.7.0-MERGED-FIG)
Strengths:

✅ Safe merge: try/except for all optional modules
✅ FIG integration: title, version, /api/fig/health, FigApp com.hellofig.FigApp, hellofig.io
✅ Minimal requirements: 3 core deps, avoids P-014
✅ 8 endpoints: /, /health, /ready, /api/health, /api/copilot/health, /api/files/health, /api/fig/health, /api/fig/app
✅ SUPABASE_SERVICE_KEY fallback logic
Gaps vs Production (from PROBLEMS.md lessons):

❌ No CORS config from env (hardcoded allowed_origins missing)
❌ No security headers (X-Frame-Options, CSP, HSTS)
❌ No rate limiting (slowapi commented)
❌ No structured logging / request ID
❌ No metrics / Prometheus
❌ No Pydantic Settings validation (OAUTH_CLIENT_ID required issue P-009)
❌ No tests (root tests/ never collects per P-009)
❌ No Dockerfile hardening (non-root, multi-stage)
❌ No CI workflows with pinned SHAs (P-002)
Roadmap
v1.8.0-SECURE — Next (Immediate)
Focus: Security + Observability without breaking safe merge

Security Middleware:
Add CORSMiddleware with env CORS_ORIGINS (from .env.example)
Add TrustedHostMiddleware
Add security headers middleware (custom)
Keep safe: try/except for slowapi
Observability:
Request ID middleware (X-Request-ID)
Structured JSON logging
/metrics endpoint (optional, only if prometheus_client installed)
Enhanced /api/health with latency
Pydantic Settings:
Create core/config.py safe version with defaults for OAUTH_CLIENT_ID (avoid P-009)
Use Settings with extra="allow"
Rate Limiting (Optional):
Uncomment slowapi if available, safe fallback
v1.9.0-TESTED — After
Add tests/ that actually collect: conftest with env defaults
Add pytest.ini, requirements-dev.txt
Fix P-009 pattern: give OAUTH_CLIENT_ID default = "test-client-id"
Add coverage gate
v2.0.0-PRODUCTION — Future
Multi-stage Dockerfile (python:3.11-slim, non-root)
docker-compose with Postgres, Redis, MinIO
GitHub Workflows with full SHA pinning (avoid P-002, P-013 fabricated SHAs)
Helm chart
Immediate Implementation — main.py v1.8.0-SECURE-FIG
Proposed changes to main.py:

python
VERSION = "1.8.0-SECURE-FIG"  # bump from 1.7.0-MERGED-FIG

# Add:
- CORS_ORIGINS from env (comma-separated)
- Security headers middleware
- Request ID middleware
- Logging setup
- Optional metrics
- Enhanced health with uptime
- Keep FIG integration
- Keep safe imports
Keep backward compatible: all existing 8 endpoints still work, new ones additive.

Files to Create Next
core/config.py — Safe Settings with defaults (fix P-009)
core/security.py — Security headers middleware
core/logging.py — Structured logging
api/v1/health.py — Expanded health logic
Dockerfile — Multi-stage, non-root
docker-compose.yml — Local stack
.github/workflows/ci.yml — Pinned SHAs, no fabricated SHAs
tests/test_health.py — Test that collects
requirements-dev.txt
FIG Agent Next
Add FIG skill: fig-agent that reads /api/fig/health and auto-discovers
Link hellofig.io connectors: Fig Connectors
Voice Mode (from hellofig.io blog Jun 10 2026)
Scheduled Tasks
How to Contribute to Next
bash
git checkout -b feat/v1.8.0-secure-fig
# Apply main.py v1.8.0
cp main_v1.8.0.py backend/main.py
pip install slowapi prometheus_client  # optional
uvicorn backend.main:app --reload
curl http://localhost:8000/api/fig/health | jq
References
PROBLEMS.md P-014, P-001, P-002, P-009, P-013
hellofig.io: https://hellofig.io/blog — Voice Mode, Scheduled Tasks, Expert Packages, Connectors
Fig App: https://play.google.com/store/apps/details?id=com.hellofig.FigApp
