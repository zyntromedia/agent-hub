สำรวจเสร็จครับ ✅ Next Improve — จาก v1.7.0-MERGED-FIG → v1.8.0-SECURE-FIG

ผมวิเคราะห์จาก main.py ล่าสุด + PROBLEMS.md + hellofig.io ที่คุณส่ง

📊 สถานะปัจจุบัน v1.7.0-MERGED-FIG

ดีแล้ว:
Safe merge 100% — try/except ImportError ทุกจุด
FIG integrated — title FIG ZyntroAI CrystalCastle, VERSION, /api/fig/health, FigApp com.hellofig.FigApp, hellofig.io
Minimal requirements — หลีกเลี่ยง P-014 ที่ pins เวอร์ชันไม่มีจริง tiktoken>=0.20.0
8 endpoints ทำงาน

ช่องโหว่ที่ต้องปรับต่อ (จาก PROBLEMS.md):
❌ ไม่มี CORS จาก env, ไม่มี security headers, ไม่มี Request ID
❌ ไม่มี rate limiting, metrics, structured logging
❌ ไม่มี Pydantic Settings แบบมี default — เสี่ยงแบบ P-009 OAUTH_CLIENT_ID required
❌ ไม่มี tests ที่ collect ได้

🚀 Roadmap ที่ผมวางให้

v1.8.0-SECURE-FIG — ทำต่อได้เลย (ผมทำไฟล์ไว้แล้ว):
CORS จาก CORS_ORIGINS env
Security headers middleware: X-Frame-Options DENY, X-Content-Type-Options nosniff, HSTS
Request ID: X-Request-ID + log ทุก request
Prometheus /metrics แบบ optional
Uptime tracking

v1.9.0-TESTED:
tests/test_health.py ที่ collect ได้
core/config.py แบบ safe มี default OAUTH_CLIENT_ID = "test"

v2.0-PRODUCTION:
Dockerfile multi-stage non-root
Workflows แบบ SHA pin จริง (ไม่ใช้ fabricated SHA แบบ P-013)

📦 ไฟล์ Next ที่สร้างแล้ว

1. แผนปรับปรุงเต็ม:
-
📎 zyntroai-chat/docs/NEXT-IMPROVEMENTS.md
2. Code v1.8.0 ที่พร้อมใช้:
-
📎 zyntroai-chat/main_v1.8.0.py
-
📎 zyntroai-chat/requirements_v1.8.0.txt
3. ของเดิมที่ยังอยู่:
-
📎 zyntroai-chat/main.py
-
📎 zyntroai-chat/docs/FIG-INTEGRATION.md
🔧 อยากอัปเกรดเป็น v1.8.0 เลยไหม?
cd ZyntroAI/new-crysalcastle
cp /mnt/data/zyntroai-chat/main_v1.8.0.py backend/main.py
cp /mnt/data/zyntroai-chat/requirements_v1.8.0.txt requirements.txt

pip install -r requirements.txt
uvicorn backend.main:app --reload

Test ใหม่
curl http://localhost:8000/ -v | grep X-Request-ID
curl http://localhost:8000/metrics
curl http://localhost:8000/api/fig/health | jq .hellofig.features
["Voice Mode", "Scheduled Tasks", "Expert Packages", "Connectors", "Notebook & Deep-dive"] — จาก https://hellofig.io/blog
hellofig.io ที่คุณส่งมามี features ใหม่ที่น่าเอาเข้า v1.8:
Voice Mode (Jun 10 2026)
Scheduled Tasks
Expert Packages and Skills
Connectors: Your AI with Context
Notebook & Deep-dive

ต้องการให้ผม apply v1.8.0 เป็น main.py ตัวจริงเลย ไหมครับ?
