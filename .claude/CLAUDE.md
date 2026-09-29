เพิ่ม section นี้ใน CLAUDE.md เพื่อบังคับให้ทุก Deployment รองรับ Automatic Rollback:

## Automatic Rollback Standards

All production deployments must support automatic rollback.

Rollback must occur without human intervention when deployment health checks fail.

---

### Rollback Triggers

Automatic rollback is required when:

- Readiness Probe fails
- Liveness Probe fails
- Smoke Test fails
- Health Endpoint fails
- Error rate exceeds threshold
- Deployment timeout exceeded
- Critical business verification fails

---

### Health Check Requirements

Every application must expose:

GET /health

Response:

```json
{
  "status": "ok"
}


Requirements:

Response time less than 500ms
No database write operations
No side effects
Kubernetes Rollout Verification

Example:

- name: Verify Rollout
  run: |
    kubectl rollout status \
      deployment/crystalcastle-api \
      --timeout=180s


Rollback on failure:

- name: Rollback
  if: failure()
  run: |
    kubectl rollout undo deployment/crystalcastle-api

Helm Auto Rollback

Recommended deployment method.

Example:

helm upgrade \
  crystalcastle-api \
  ./helm \
  --install \
  --atomic \
  --wait \
  --timeout 5m


Requirements:

Use --atomic
Use --wait
Define timeout

Benefits:

Auto rollback
Deployment verification
Single command recovery
GitHub Actions Rollback Example

File:

.github/workflows/deploy-production.yml

jobs:

  deploy:

    runs-on: ubuntu-latest

    steps:

      - name: Deploy
        run: |
          helm upgrade \
            crystalcastle-api \
            ./helm \
            --install \
            --atomic \
            --wait \
            --timeout 5m

      - name: Smoke Test
        run: |
          curl --fail https://api.example.com/health

      - name: Rollback
        if: failure()
        run: |
          helm rollback crystalcastle-api

Progressive Verification

Deployment Success Criteria:

Pod Running
Readiness Passing
Service Reachable
Health Endpoint Healthy
Smoke Test Passing
Error Rate Normal
No CrashLoopBackOff

Deployment is considered FAILED if any step fails.

Blue-Green Rollback

Preferred for critical systems.

Flow:

Current Production (Blue)

Deploy Green

Run Verification

If Success: Switch Traffic → Green

If Failure: Keep Traffic → Blue

Result:

Users never see failed deployment.

Canary Rollback

For higher-risk releases:

Traffic Distribution:

10% → Verify

25% → Verify

50% → Verify

100% → Verify

Rollback immediately if:

Error rate spike
Latency spike
Availability degradation
Smoke Test Gates

Required post-deploy checks:

Authentication
Main API
Database connection
Redis connection
Critical business endpoint

Example:

curl --fail https://api.example.com/health
curl --fail https://api.example.com/auth/status
curl --fail https://api.example.com/version

Observability Requirements

Required monitoring:

Prometheus
Grafana
Alertmanager

Track:

Error Rate
Latency
CPU
Memory
Restart Count
Deployment Failure Count
Deployment Recovery Objective

Targets:

RTO: < 5 minutes

Rollback: < 2 minutes

Detection: < 1 minute

AI Agent Rollback Rules

When generating deployment workflows:

Automatic rollback is mandatory.
Helm deployments must use --atomic.
Rollback path must be tested.
Health checks must exist.
Smoke tests must exist.
Deployments must fail fast.
Never disable rollout verification.
Never continue after failed health checks.
Rollback logic must be included in production workflows.
Recovery procedures must be documented.
Definition of Done

A deployment is complete only when:

Deployment successful
Health checks passing
Smoke tests passing
Monitoring healthy
Rollback available
Rollback tested

### แนะนำเพิ่มเติมสำหรับ CrystalCastle X

เพิ่มกฎระดับ Production อีกอัน:

```md
### Deployment Safety Policy

Production deployment must use:

✅ Helm --atomic
✅ Readiness Probe
✅ Liveness Probe
✅ Startup Probe
✅ Smoke Tests
✅ Rollback Verification

Forbidden:

❌ kubectl apply directly to production
❌ continue-on-error
❌ skip health checks
❌ force deployment
❌ manual hotfix deployment

If rollback fails, deployment must be marked FAILED.


กฎนี้จะทำให้ Claude Code, Copilot Coding Agent และ AI Agent อื่น ๆ สร้าง workflow แบบ "deploy-safe by default" โดยมี rollback อัตโนมัติทุกครั้งที่ health check, smoke test หรือ rollout verification ล้มเหลว.
