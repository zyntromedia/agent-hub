# agent-hub

[![CI](https://github.com/zyntromedia/agent-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/zyntromedia/agent-hub/actions/workflows/ci.yml)
[![Docker CI/CD](https://github.com/zyntromedia/agent-hub/actions/workflows/docker-ci.yml/badge.svg)](https://github.com/zyntromedia/agent-hub/actions/workflows/docker-ci.yml)
[![CodeQL](https://github.com/zyntromedia/agent-hub/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/zyntromedia/agent-hub/actions/workflows/codeql-analysis.yml)

> Frontend for an AI agent hub — orchestrate LLM agents, route models via OpenRouter, and manage billing with Stripe.

## ✨ Features

- Multi-agent chat / orchestration UI (React + shadcn/ui + Tailwind)
- LLM routing through **OpenRouter** (swap providers/models without code changes)
- Stripe payments + subscription gating
- TypeScript, ESLint, Vitest — fully typed and tested
- Production build via webpack, served by nginx (unprivileged, ~25 MB image)
- Deployable to Kubernetes (manifests included) with HPA autoscaling
- SBOM generation + dependency-graph submission on every build

## 🧰 Tech Stack

| Layer | Choice |
|---|---|
| UI | React 18, shadcn/ui, Tailwind CSS, Framer Motion |
| Language | TypeScript (type-checked via `tsc`) |
| Dev server | Vite |
| Production build | webpack |
| Tests | Vitest |
| Package manager | **pnpm** (`packageManager: pnpm@7.5.1` — see note below) |
| LLM gateway | OpenRouter (optional: Google GenAI / Vertex) |
| Payments | Stripe |
| Backend-as-a-service | base44 SDK |
| Container | nginx-unprivileged (multi-stage build) |
| Infra | Kubernetes (`k8s-deployment.yaml`, `k8s-hpa.yaml`) |

> **Note:** `pnpm@7.5.1` is pinned in `package.json` but predates Node 22. Consider bumping to `pnpm@9.x` and refreshing `pnpm-lock.yaml`.

## 🚀 Quick Start

### Prerequisites
- Node.js >= 18 (22 LTS recommended)
- pnpm (`corepack enable` then `corepack prepare pnpm@7.5.1 --activate`, or `npm i -g pnpm`)

### Install & run
```bash
# 1. Clone
git clone https://github.com/zyntromedia/agent-hub.git
cd agent-hub

# 2. Environment
cp .env.example .env   # then fill in your keys (see below)

# 3. Install (strict, lockfile-pinned — equivalent to npm ci)
pnpm install --frozen-lockfile

# 4. Dev server (Vite, http://localhost:5173)
pnpm dev
```

### Scripts
| Command | Description |
|---|---|
| `pnpm dev` | Vite dev server |
| `pnpm build` | Production webpack build → `dist/` |
| `pnpm preview` | Preview production build locally |
| `pnpm test` | Run Vitest (once) |
| `pnpm test -- --coverage` | Run tests with coverage report |
| `pnpm lint` | ESLint (`. --quiet`) |
| `pnpm lint:fix` | Auto-fix lint issues |
| `pnpm typecheck` | `tsc -p ./jsconfig.json` |

## 🔐 Environment Variables

Copy `.env.example` → `.env` and fill in. **Never commit `.env`.**

Key variables:
- `OPENROUTER_API_KEY` — **secret**, LLM gateway key (server-side only)
- `VITE_API_URL` — backend API base URL (client-safe, baked into bundle)
- `INTERNAL_API_KEY` — **secret**, service-to-service auth
- `VITE_STRIPE_PUBLISHABLE_KEY` / `STRIPE_SECRET_KEY` — payments
- `VITE_BASE44_APP_ID` — base44 backend app ID

Full list in [`.env.example`](./.env.example). Any variable prefixed `VITE_` is public (shipped in the browser bundle) — never put secrets there.

## 🐳 Docker

```bash
docker build -t agent-hub:local .
docker run --rm -p 8080:8080 \
  --build-arg VITE_API_URL=https://api.example.com \
  agent-hub:local
# → http://localhost:8080
```
Multi-stage build: `node:22-alpine` (pnpm + webpack) → `nginxinc/nginx-unprivileged:alpine`. SPA fallback + asset caching in `nginx.conf`.

## ☸️ Kubernetes

Manifests in repo root:
- `k8s-deployment.yaml` — Deployment + Service (port 8080)
- `k8s-hpa.yaml` — HorizontalPodAutoscaler (CPU/memory based)

```bash
kubectl apply -f k8s-deployment.yaml -f k8s-hpa.yaml
```

## 🔄 CI/CD (`.github/workflows/`)

| Workflow | Purpose |
|---|---|
| `ci.yml` | lint → typecheck → test+coverage → build |
| `docker-ci.yml` | lint/test/build gate → build & push image to GHCR |
| `api-security.yml` | API security test gate |
| `codeql-analysis.yml` | CodeQL SAST |
| `sbom-upload.yml` | SBOM (CycloneDX/SPDX) → Dependency Graph + release assets |
| `ci-unified.yml` | Full pipeline + GitHub Pages deploy + semantic-release |

## 📁 Project Structure (high level)

```
agent-hub/
├── src/                  # React app source
├── public/               # static assets
├── .github/workflows/    # CI/CD
├── k8s-*.yaml            # Kubernetes manifests
├── Dockerfile / nginx.conf / .dockerignore
├── auth_reference.py     # Python auth reference (bcrypt/passlib)
└── package.json          # pnpm-based
```

## 🛡️ Security

- Secrets are never committed (`.env` git-ignored; `.env.example` is the template)
- Dependencies pinned via `pnpm-lock.yaml`; SBOM generated per build
- CodeQL + API security gates run on every PR
- Auth reference uses bcrypt (see `auth_reference.py`); passwords are never logged

## 🤝 Contributing

1. Fork & branch from `main`
2. `pnpm install --frozen-lockfile`
3. Ensure `pnpm lint`, `pnpm typecheck`, and `pnpm test` pass
4. Open a PR — all CI gates must be green

## 📄 License

<!-- TODO: set your license, e.g. MIT / Apache-2.0 -->
