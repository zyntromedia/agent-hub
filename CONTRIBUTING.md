ได้เลยครับ! นี่คือ CONTRIBUTING.md ฉบับปรับปรุงเต็มรูปแบบ — ครอบคลุม • มาตรฐาน • ปลอดภัย • ใช้งานง่าย 📝✅🚀
 
 
 
🤝 CONTRIBUTING.md — ZyntroMedia / Agent Hub
 
markdown
  
# Contributing to Agent Hub

ขอบคุณที่สนใจช่วยพัฒนา **Agent Hub**! 🎯🎉  
ศูนย์รวม AI Agents, Skills และ Tools — เป้าหมายคือให้ทุกคนเพิ่ม/แก้ไขได้ง่าย รวดเร็ว และปลอดภัย

---

## 📋 สารบัญ
- [🚀 เริ่มต้นอย่างรวดเร็ว](#-เริ่มต้นอย่างรวดเร็ว)
- [📂 โครงสร้างโปรเจกต์](#-โครงสร้างโปรเจกต์)
- [🧠 วิธีเพิ่ม Agent / Skill ใหม่](#-วิธีเพิ่ม-agent--skill-ใหม่)
- [✅ มาตรฐานการเขียนโค้ด](#-มาตรฐานการเขียนโค้ด)
- [🔐 ความปลอดภัย](#-ความปลอดภัย)
- [📥 ขั้นตอนส่ง Pull Request](#-ขั้นตอนส่ง-pull-request)
- [🐛 รายงานปัญหา](#-รายงานปัญหา)

---

## 🚀 เริ่มต้นอย่างรวดเร็ว

### 1. Fork & Clone
```bash
git clone https://github.com/zyntromedia/agent-hub.git
cd agent-hub
 
 
2. ติดตั้ง
 
bash
  
npm install
cp .env.example .env
 
 
3. กำหนดค่า
 
แก้ไข  .env  — ใส่คีย์ของคุณ:
 
env
  
PORT=3000
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
 
 
⚠️ ห้าม commit ไฟล์  .env  เด็ดขาด — มี  .gitignore  ป้องกันไว้แล้ว ✅
 
4. รันระบบ
 
bash
  
npm run dev
# Server ที่: http://localhost:3000
 
 
 
 
📂 โครงสร้างโปรเจกต์
 
plaintext
  
agent-hub/
├── src/
│   ├── agents/          # 🧠 คำนิยาม Agent — เพิ่มตรงนี้
│   ├── skills/          # 🛠️ ทักษะ/โมดูลนำกลับมาใช้ซ้ำ
│   ├── routes/          # 📡 API Endpoints
│   ├── lib/             # 🔧 Client, Utils, Helpers
│   └── index.ts         # 🚀 จุดเริ่มต้นระบบ
├── .github/workflows/   # ⚙️ CI/CD — ตรวจสอบอัตโนมัติ
├── .env.example         # 📋 แม่แบบตัวแปรสภาพแวดล้อม
├── .dockerignore
├── Dockerfile
└── package.json
 
 
 
 
🧠 วิธีเพิ่ม Agent ใหม่ — ภายใน 5 นาที
 
ขั้นตอนที่ 1: สร้างไฟล์
 
สร้าง  src/agents/ชื่อ-agent.ts :
 
typescript
  
export const yourAgent = {
  name: "your-agent",
  description: "อธิบายว่า Agent นี้ทำอะไร",
  model: "openai/gpt-4o-mini", // เลือกโมเดลจาก OpenRouter
  systemPrompt: `บทบาทของคุณคือ...`,
  run: async (input: string) => {
    // ตรรกะการทำงาน
    return { response: `ได้รับ: ${input}` };
  },
};
 
 
ขั้นตอนที่ 2: ลงทะเบียน
 
แก้ไข  src/agents/index.ts :
 
typescript
  
export * from "./your-agent.js";
 
 
ขั้นตอนที่ 3: ทดสอบ
 
bash
  
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"agent":"your-agent","message":"สวัสดี"}'
 
 
✅ ถ้าตอบกลับมา = พร้อมส่งแล้ว!
 
 
 
✅ มาตรฐานการเขียนโค้ด
 
ข้อกำหนด คำสั่งตรวจสอบ 
ภาษา TypeScript + ESM ( "type": "module" ) 
รูปแบบโค้ด  npm run format  
ตรวจสอบข้อผิดพลาด  npm run lint  — ต้องผ่านก่อนส่ง PR 
ทดสอบ  npm test  (ถ้ามี) 
คอมมิต Conventional Commits —  feat: ,  fix: ,  docs: ,  chore:  
Docker  docker build -t agent-hub .  ต้องผ่าน ✅ 
 
รูปแบบข้อความคอมมิต
 
plaintext
  
feat: เพิ่ม Agent สรุปเนื้อหาอัตโนมัติ
fix: แก้ไขข้อผิดพลาดเมื่อ API คืนค่าว่าง
docs: อัปเดตคู่มือการติดตั้ง
chore: อัปเดต js-yaml เป็น 4.3.2
 
 
 
 
📥 ขั้นตอนส่ง Pull Request
 
1️⃣ สร้างสาขาใหม่
 
bash
  
git checkout -b feat/add-your-agent
 
 
2️⃣ ตรวจสอบก่อนส่ง
 
bash
  
npm run lint
npm run format
# แก้ไขจนกว่าจะไม่มีข้อความแจ้งเตือน
 
 
3️⃣ คอมมิต & ส่ง
 
bash
  
git add .
git commit -m "feat: add your-agent — สรุปสั้นๆ"
git push -u origin feat/add-your-agent
 
 
4️⃣ เปิด PR บน GitHub
 
- อธิบาย: ทำอะไร + ตัวอย่างใช้งาน
- ตรวจสอบ: CI ทั้งหมดต้องเขียว ✅
- รอ: ผู้ดูแลตรวจสอบ & อนุมัติ
 
 
 
🔐 ความปลอดภัย
 
- ❌ ห้าม commit ไฟล์  .env  หรือคีย์ส่วนตัว
- ❌ ห้าม เขียนคีย์/โทเคนลงในโค้ดโดยตรง
- ✅ ใช้  ${{ secrets.NAME }}  สำหรับ GitHub Actions
- ✅ ใช้  .env  ในเครื่อง +  .env.example  เฉพาะรูปแบบ
- 📧 พบช่องโหว่แจ้ง: security@zyntro.media — ไม่เปิดเป็น Issue สาธารณะ
 
 
 
🐛 รายงานปัญหา
 
เปิด Issue แล้วระบุ:
 
- หัวข้อ: ปัญหาที่พบแบบสั้นๆ
- ขั้นตอนเกิด: วิธีทำให้เกิดข้อผิดพลาด
- ผลลัพธ์ที่ได้: ข้อความแจ้งเตือน/ภาพหน้าจอ
- สภาพแวดล้อม: เวอร์ชัน Node, ระบบปฏิบัติการ
 
 
 
💬 มีคำถาม?
 
- สนทนา: GitHub Discussions
- แจ้งปัญหา: Issues
- ติดต่อทีม: hello@zyntro.media
 
 
 
ขอบคุณที่ช่วยทำให้ Agent Hub เติบโตและดีขึ้นทุกวันนะครับ 🙌🚀
 
plaintext
  

---

## 🚀 คำสั่งอัปเดตไฟล์
```bash
# บันทึกไฟล์
cat > CONTRIBUTING.md << 'EOF'
<เนื้อหาด้านบน>
EOF

# ตรวจสอบ
ls -la CONTRIBUTING.md

# คอมมิต
git add CONTRIBUTING.md
git commit -m "docs: completely rewrite CONTRIBUTING.md — structured, bilingual, security-first

- Clear 5-minute quick-start guide ✅
- Project structure overview ✅
- Step-by-step agent creation template ✅
- Coding standards & commit message examples ✅
- Security policy — no secrets committed ✅
- Full PR workflow explained ✅
- Bug report template ✅
- Contact links updated ✅"

git push origin main
 
 
 
 
✅ ปรับปรุงที่เพิ่มขึ้นจากฉบับเดิม
 
ก่อน หลัง 
เนื้อหากระจาย ไม่มีโครงสร้าง มีสารบัญ + แยกส่วนชัดเจน ✅ 
ไม่มีตัวอย่างโค้ดเต็มรูปแบบ มีเทมเพลต Agent พร้อมคัดลอกใช้ ✅ 
ไม่เน้นความปลอดภัย แยกส่วน Security ชัดเจน + ห้ามรั่วคีย์ ✅ 
ไม่มีรูปแบบคอมมิต ตัวอย่าง Conventional Commits ครบถ้วน ✅ 
ภาษาผสมไม่สม่ำเสมอ จัดระเบียบ สอดคล้องกันทั้งเอกสาร ✅ 
ไม่มีขั้นตอนทดสอบ คำสั่ง curl ตรวจสอบระบบทำงานจริง ✅ 
 
พร้อมใช้งานเลยครับ! ต้องการปรับเพิ่มส่วนไหนไหมครับ 🎯✅🚀4.  CI ต้องเขียว: build + lint
5.  รอ Review จาก Maintainer

## รายงาน Bug
เปิด Issue แล้วใส่:
- ขั้นตอนการ reproduce
- Log error
- เวอร์ชัน Node, OS

## Security
ห้าม commit `.env` หรือ `OPENROUTER_API_KEY` เด็ดขาด
เจอช่องโหว่แจ้งที่ security@zyntro.media

---

มีคำถาม? มาคุยกันใน Discussions ได้เลย
ขอบคุณที่ช่วยทำให้ agent-hub เก่งขึ้นนะครับ 🙌

### **ไฟล์ที่ควรมีคู่กัน**
1.  **`.env.example`**
    ```env
    PORT=3000
    OPENROUTER_API_KEY=sk-or-v1-your-key-here
2.  *`.dockerignore`*
    node_modules
    .git
    .env
เอาไปวางแล้ว PR แรกของ contributor จะง่ายขึ้นเยอะเลย

อยากให้ผมเพิ่มส่วน "Code of Conduct" หรือ "Good First Issues" ให้ด้วยไหมคะ?
