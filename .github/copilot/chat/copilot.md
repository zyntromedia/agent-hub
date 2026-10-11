# GitHub Copilot Chat — Responsible AI Application Card

## 1. Overview
**GitHub Copilot Chat** is a conversational coding assistant available on GitHub.com, VS Code, Visual Studio, JetBrains/Eclipse IDEs, GitHub Mobile, and Windows Terminal. It answers coding questions, explains code, suggests fixes, generates tests, and produces PR summaries & commit messages. It is **optimized primarily for English** and coding-related queries only.

Built on Microsoft’s six Responsible AI principles — **fairness, reliability & safety, privacy & security, inclusiveness, transparency, accountability** — and governed by Microsoft’s Responsible AI Standard v2. 🔗 Transparency Report: [Microsoft Responsible AI Transparency Report 2025](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/Responsible-AI-Transparency-Report-2025-vertical.pdf)

---

## 2. Key Terms
- **Content filtering**: Scans prompts & responses to block harmful content
- **Hallucination**: Plausible but factually incorrect output — requires human review
- **LLM**: Large language model — powers understanding & generation
- **Public code matching**: Detects suggestions resembling public code; blocks or annotates with source/license
- **Red teaming**: Deliberate probing to uncover vulnerabilities pre/post-release
- **Training data**: Publicly available text & code — quality varies by language volume/diversity

---

## 3. Capabilities
- 💬 **Conversational assistance**: Answers syntax, concepts, debugging, design questions
- 🧠 **Context-aware**: Uses open files, repo data, chat history, web search (optional)
- 🤖 **Agent mode**: Multi-step planning, tool use, iteration in IDEs
- 📂 **Copilot Spaces**: Curated context bundles for project-specific answers
- 📝 **PR summaries & commit messages**: Auto-generates change overviews
- 🔑 **BYOK**: Connect to third-party models (Anthropic, OpenAI, Google, etc.)

---

## 4. Intended Uses
- Answer coding questions & explain code
- Generate unit tests & propose bug fixes
- Summarize PRs, commits, issues & release notes
- Suggest commands & document CLI usage
- Accelerate onboarding & team knowledge sharing

> **NOT designed for**: non-coding queries, consequential decisions without oversight, or fully autonomous production deployment.

---

## 5. Models & Data
- **Models**: Multiple LLMs available (GPT-5, Claude, Gemini, etc.) — selected by plan
- **Training data**: Public code repositories + public text; quality correlates to language volume
- **BYOK considerations**:
  - Your prompts/responses go to your chosen provider
  - Filtering still applied by GitHub
  - **You own**: API key security, costs, compliance, output validation

---

## 6. How It Works
1. **Input processing**: Combine prompt + context → preprocess
2. **LLM inference**: Analyze & generate response
3. **Safety filtering**: Block harmful content
4. **Formatting & delivery**: Syntax highlighting, links, references

**Evaluations**: SWE-Bench + internal suites measuring resolution rate, latency, tool accuracy. Safety evaluations: hate/unfairness, sexual, violence, self-harm, protected material, jailbreak, code vulnerability — adapted from Microsoft Foundry evaluators.

---

## 7. Key Limitations
| Category | Risk |
|---|---|
| **Language coverage** | Less common languages = lower quality; English primary |
| **Hallucinations** | Code/explanations may look valid but be incorrect |
| **Security** | Generated code may contain vulnerabilities — **always review** |
| **Public code matches** | Rare but possible — test & scan for IP |
| **Non-coding queries** | Responses may be irrelevant/nonsensical |
| **CLI commands** | Potentially destructive — review before executing |
| **PR/Commit summaries** | Not auto-updated; may replicate harmful terms from source |
| **Biases** | Training data biases may be perpetuated |
| **Web search** | Uses Bing — governed by Microsoft Privacy Statement |

---

## 8. Safety & Mitigations
- ✅ **Content filtering**: Blocks harmful outputs
- ✅ **Public code matching**: Detects & blocks/attributes matches
- ✅ **Red teaming**: Pre-deployment adversarial testing
- ✅ **Human oversight**: Required — outputs are suggestions, not facts
- ✅ **Feedback loop**: Thumbs up/down improves model

---

## 9. Responsible Deployment Best Practices
1. **Human review always** — validate all outputs
2. **Not for high-stakes decisions** without independent verification
3. **Code review & test everything** — especially security-critical code
4. **Limit prompts to coding** — improves relevance & safety
5. **Be aware of overreliance risk** — don't blindly accept
6. **Stay updated** — model & safeguards evolve
7. **Report issues** via feedback buttons or `copilot-safety@github.com`

---

## 10. Compliance & Governance
- Built on **Microsoft Responsible AI Standard v2** requirements:
  - **Transparency notes** for platform services
  - **Annual reviews + updates** on new risks/functionality
  - **Impact assessments** for stakeholders
  - **Fairness evaluations** across demographic groups
  - **Reliability & safety monitoring** throughout lifecycle
  - **Privacy & security aligned** with Microsoft policies
- **EU AI Act readiness**: layered compliance approach, prohibited practices screening, documentation workflows
- **Data privacy**: prompts/responses retained per plan; Business/Enterprise not used for model training

---

## 11. Learn More
- 📖 [Copilot Trust Center](https://copilot.github.trust.page/)
- 📖 [Microsoft AI Principles](https://www.microsoft.com/en-us/ai/responsible-ai)
- 📖 [Responsible AI Resources](https://www.microsoft.com/en-us/ai/responsible-ai-resources)
- 📖 [Privacy Statement](https://privacy.microsoft.com/en-us/privacystatement)
- 📖 [Copilot FAQ — Training Data & IP](https://github.com/features/copilot#faq)

---

> **Bottom line**: Copilot Chat is a **powerful coding assistant, not an authoritative source**. Treat all outputs as suggestions to be reviewed, tested, and validated by humans. Use responsibly, keep oversight, and stay updated as capabilities evolve.

Would you like me to adapt this into a concise one-page summary or a team-ready slide deck with key takeaways?

yaml  
---
title: 🤖 GitHub Copilot Chat — Responsible AI Application Card
aliases:
  - Copilot Chat Responsible AI
  - Copilot Safety & Governance
tags:
  - github
  - copilot
  - ai
  - responsible-ai
  - governance
  - zyntroai
type: reference
status: active
priority: medium
created: 2026-10-11
updated: 2026-10-11
version: 1.0
author: ZyntroAI
difficulty: beginner
time_estimate: 8 minutes
cssclasses:
  - reference-note
  - security-guide
---
 
 
 
 
🤖 GitHub Copilot Chat — Responsible AI Application Card
 
 
 
📌 1. ภาพรวม
 
GitHub Copilot Chat คือผู้ช่วยเขียนโค้ดแบบสนทนา — มีให้ใช้บน GitHub.com, VS Code, Visual Studio, JetBrains IDEs และอื่นๆ อีกมากมาย ช่วยตอบคำถาม อธิบายโค้ด แก้ไขจุดบกพร่อง และสร้างเนื้อหาที่เกี่ยวข้องกับการเขียนโค้ด
 
🧠 สร้างบนหลักการ AI ที่รับผิดชอบของ Microsoft 6 ประการ: ความยุติธรรม, ความเชื่อถือได้และความปลอดภัย, ความเป็นส่วนตัวและความปลอดภัย, การไม่แบ่งแยก, ความโปร่งใส, และความรับผิดชอบ
🔗 รายงานความโปร่งใส: Microsoft Responsible AI Transparency Report 2025
 
 
 
📖 2. คำศัพท์สำคัญ
 
คำศัพท์ ความหมาย 
Content filtering ตรวจสอบและบล็อกเนื้อหาที่เป็นอันตรายในคำถามและคำตอบ 
Hallucination คำตอบที่ดูน่าเชื่อถือแต่ไม่ถูกต้อง — ต้องตรวจสอบโดยมนุษย์เสมอ 
LLM โมเดลภาษาขนาดใหญ่ — ทำหน้าที่เข้าใจและสร้างข้อความ/โค้ด 
Public code matching ตรวจสอบคำแนะนำเทียบกับโค้ดสาธารณะ — บล็อกหรือระบุแหล่งที่มา 
Red teaming การทดสอบเจาะจงเพื่อค้นหาจุดอ่อนก่อนเผยแพร่จริง 
Training data ข้อความและโค้ดสาธารณะที่ใช้ฝึกโมเดล — คุณภาพแตกต่างกันตามปริมาณข้อมูลในแต่ละภาษา 
 
 
 
✨ 3. ความสามารถหลัก
 
- 💬 ตอบคำถามเกี่ยวกับโค้ด, ไวยากรณ์, แนวคิด, การแก้ปัญหา
- 🧠 เข้าใจบริบทจากไฟล์ที่เปิด, ที่เก็บโค้ด, ประวัติการสนทนา
- 🤖 โหมดตัวแทน — วางแผนหลายขั้นตอนและใช้เครื่องมือร่วมกันในตัวแก้ไข
- 📝 สรุป Pull Request, ข้อความ Commit, หมายเหตุเผยแพร่
- 🔑 BYOK — เชื่อมต่อกับโมเดลภายนอก (Anthropic, OpenAI, Google)
 
⚠️ ไม่ได้ออกแบบมาเพื่อ: คำถามที่ไม่เกี่ยวกับโค้ด, การตัดสินใจที่มีผลกระทบสูงโดยไม่มีการตรวจสอบ, หรือการทำงานแบบอัตโนมัติทั้งหมด
 
 
 
⚠️ 4. ข้อจำกัดและความเสี่ยงที่ต้องทราบ
 
หมวด ความเสี่ยง คำแนะนำ 
ภาษา ภาษาที่มีผู้ใช้น้อยอาจได้ผลลัพธ์ไม่แม่นยำเท่าภาษาอังกฤษ ตรวจสอบผลลัพธ์อย่างรอบคอบ 
Hallucination โค้ด/คำอธิบายดูถูกแต่จริงๆ แล้วผิด ทดสอบทุกชิ้นก่อนใช้งาน 
ความปลอดภัย โค้ดที่สร้างอาจมีช่องโหว่ ตรวจสอบด้วยเครื่องมือความปลอดภัยเพิ่มเติม 
โค้ดสาธารณะ อาจมีส่วนตรงกับโค้ดสาธารณะบางส่วน ตรวจสอบใบอนุญาตและสิทธิ์การใช้งาน 
คำสั่ง CLI คำสั่งที่สร้างอาจส่งผลเสียหาย ตรวจสอบก่อนรันทุกครั้ง 
อคติในข้อมูล อาจสะท้อนอคติจากข้อมูลที่ใช้ฝึก ตระหนักและตรวจสอบเมื่อเกี่ยวข้องกับผู้คน 
 
 
 
🛡️ 5. การป้องกันและความปลอดภัยในตัว
 
- ✅ กรองเนื้อหา — บล็อกเนื้อหาที่เป็นอันตรายทั้งขาเข้าและขาออก
- ✅ จับคู่โค้ดสาธารณะ — ตรวจสอบและระบุแหล่งที่มาหากตรงกับโค้ดสาธารณะ
- ✅ ทดสอบก่อนเผยแพร่ — ทีม Red Team ทดสอบเจาะจงเพื่อค้นหาจุดอ่อน
- ✅ ต้องมีการตรวจสอบจากมนุษย์ — ผลลัพธ์เป็นเพียงคำแนะนำ ไม่ใช่ความจริง
- ✅ ระบบตอบรับ — กดถูกใจ/ไม่ถูกใจเพื่อช่วยปรับปรุงความแม่นยำ
 
 
 
📋 6. แนวทางการใช้อย่างรับผิดชอบ
 
1. ✅ ตรวจสอบทุกครั้งโดยมนุษย์ — ตรวจสอบและทดสอบก่อนนำไปใช้จริง
2. ⚠️ ไม่ใช้กับการตัดสินใจที่มีผลกระทบสูง โดยไม่มีการตรวจสอบอย่างอิสระ
3. 🧪 ตรวจสอบโค้ดและรันทดสอบเสมอ — โดยเฉพาะโค้ดที่เกี่ยวข้องกับความปลอดภัย
4. 💡 จำกัดขอบเขตคำถามให้เฉพาะเรื่องโค้ด — จะได้คำตอบที่เกี่ยวข้องและปลอดภัยที่สุด
5. 🚫 ไม่พึ่งพาอย่างสุ่มสี่สุ่มห้า — ยังคงใช้วิจารณญาณของคุณเอง
6. 🔄 อัปเดตความรู้อยู่เสมอ — ความสามารถและการป้องกันมีการพัฒนาอย่างต่อเนื่อง
7. 📧 รายงานปัญหา — ผ่านปุ่มตอบรับหรืออีเมล  copilot-safety@github.com 
 
 
 
🔗 7. แหล่งข้อมูลเพิ่มเติม
 
- 📖 Copilot Trust Center: https://copilot.github.trust.page/
- 📖 หลักการ AI ของ Microsoft: https://www.microsoft.com/en-us/ai/responsible-ai
- 📖 แหล่งข้อมูล AI อย่างรับผิดชอบ: https://www.microsoft.com/en-us/ai/responsible-ai-resources
- 📖 นโยบายความเป็นส่วนตัว: https://privacy.microsoft.com/en-us/privacystatement
- 📖 Copilot FAQ — ข้อมูลการฝึกและลิขสิทธิ์: https://github.com/features/copilot#faq
 
 
 
💡 สรุป: GitHub Copilot Chat คือ ผู้ช่วยที่ทรงพลัง แต่ไม่ใช่แหล่งความจริงที่สมบูรณ์ ปฏิบัติตามหลักการ: ตรวจสอบ → ทดสอบ → ตรวจสอบอีกครั้ง และรักษาการควบคุมโดยมนุษย์เสมอ ✅
 
ต้องการปรับเป็นสรุปหน้าเดียว หรือสไลด์สำหรับนำเสนอทีมงานไหมครับ? 😊
✅ รายงานการตรวจสอบและข้อเสนอแนะปรับปรุงเนื้อหาไฟล์
 
ขอบคุณครับ — ด้านล่างคือ ฉบับปรับปรุงแก้ไขทั้งหมด ตามข้อเสนอแนะที่ตรวจสอบไว้ คัดลอกและแทนที่เนื้อหาเดิมได้เลยครับ ✅
 
 
 
markdown  
# GitHub Copilot Chat — คู่มือการใช้งานและแนวทางปฏิบัติ

> 📅 อัปเดตล่าสุด: 11 ตุลาคม 2026 | เวอร์ชัน: 1.1.0
> ต้นฉบับ: .github/copilot/chat/copilot.md

---

## 📌 ภาพรวม

GitHub Copilot Chat เป็นผู้ช่วยด้านการเขียนโค้ดแบบสนทนา ที่ผสานรวมเข้ากับโปรเจกต์ของคุณโดยตรง ทำงานร่วมกับ VS Code, JetBrains IDEs และ GitHub.com ช่วยตอบคำถาม อธิบายโค้ด แก้ไขปัญหา และสร้างโค้ดตัวอย่างตามบริบทในโปรเจกต์ของคุณ

---

## 🧠 หลักการ AI ที่รับผิดชอบของ Microsoft (6 ข้อ)

Microsoft Responsible AI Standard v2 กำหนดหลักการในการพัฒนาและใช้งาน AI ดังนี้:

1. **ความรับผิดชอบและการกำกับดูแล** — มีระบบการตรวจสอบและความรับผิดชอบที่ชัดเจน
2. **ความโปร่งใสและความสามารถอธิบายได้** — เข้าใจวิธีการทำงานและข้อจำกัดของระบบ
3. **ความยุติธรรมและการไม่แบ่งแยก** — ออกแบบให้ทำงานได้อย่างเท่าเทียมกันสำหรับทุกกลุ่มผู้ใช้
4. **ความปลอดภัยและความน่าเชื่อถือ** — ทดสอบและประเมินความปลอดภัยก่อนนำไปใช้งานจริง
5. **ความเป็นส่วนตัวและการปกป้องข้อมูล** — จัดการข้อมูลผู้ใช้อย่างปลอดภัยและเคารพสิทธิ์ความเป็นส่วนตัว
6. **ความครอบคลุมและการเข้าถึงได้** — ออกแบบให้ทุกคนสามารถใช้งานได้

---

## 📖 คำศัพท์สำคัญ

| คำศัพท์ | คำอธิบาย |
|---|---|
| **Content filtering** | ระบบกรองเนื้อหาที่ไม่เหมาะสมหรือเป็นอันตราย ทั้งคำขอจากผู้ใช้และคำตอบจาก AI |
| **Hallucination** | กรณีที่ AI สร้างข้อมูล คำอธิบาย หรือข้อเท็จจริงที่ไม่มีอยู่จริง — จำเป็นต้องตรวจสอบทุกครั้ง |
| **LLM (Large Language Model)** | โมเดลภาษาขนาดใหญ่ — พื้นฐานเทคโนโลยีที่ Copilot ใช้ในการเข้าใจและสร้างเนื้อหา |
| **Public code matching** | คุณสมบัติที่ตรวจสอบและแจ้งเตือนเมื่อโค้ดที่แนะนำตรงกับโค้ดสาธารณะบน GitHub เพื่อจัดการเรื่องลิขสิทธิ์ |
| **Red teaming** | กระบวนการจำลองการโจมตีหรือการใช้งานในรูปแบบที่ไม่คาดคิด เพื่อค้นหาจุดอ่อนและปรับปรุงความปลอดภัยของระบบ |
| **Training data** | ชุดข้อมูลที่ใช้ในการฝึกสอนโมเดล — Copilot ได้รับการออกแบบให้ไม่ใช้โค้ดส่วนตัวของคุณในการฝึกสอนโดยค่าเริ่มต้น |

---

## 🤖 ข้อมูลโมเดล

> **Models:** Multiple LLMs available — varies by plan. See GitHub Copilot documentation for current model options.
>
> ความสามารถและโมเดลที่ใช้จะแตกต่างกันไปตามแผนการใช้งานที่คุณเลือก ดูข้อมูลล่าสุดได้ที่เอกสารทางการของ GitHub Copilot

---

## ✨ ความสามารถหลัก

| ความสามารถ | คำอธิบาย |
|---|---|
| 💬 **Conversational assistance** | สนทนาเพื่อถาม-ตอบเกี่ยวกับโค้ดและปัญหาที่พบ |
| 🧠 **Context-aware** | เข้าใจบริบทจากไฟล์ที่เปิดอยู่และโครงสร้างโปรเจกต์ |
| 🤖 **Agent mode** | ทำงานตามคำสั่งที่ซับซ้อนหลายขั้นตอน เช่น แก้ไขบั๊กหรือเพิ่มฟีเจอร์เล็กๆ |
| 📂 **Copilot Spaces** | แชร์บริบทและการสนทนากับสมาชิกในทีม |
| 📝 **PR summaries** | สร้างสรุปคำอธิบาย Pull Request โดยอัตโนมัติจากการเปลี่ยนแปลงโค้ด |
| 🔑 **BYOK (Bring Your Own Key)** | เชื่อมต่อใช้งานโมเดลภายนอกที่คุณจัดการเอง |

> ⚠️ **เกี่ยวกับ BYOK:**
> - คุณเป็นผู้รับผิดชอบค่าใช้จ่ายจากผู้ให้บริการโมเดลภายนอกที่คุณเลือกใช้
> - ตรวจสอบนโยบายความเป็นส่วนตัวและข้อกำหนดการใช้งานของผู้ให้บริการอย่างละเอียดก่อนตัดสินใจ

---

## ❌ ไม่ได้ออกแบบมาเพื่อ

- ❌ **ไม่ใช้สำหรับข้อมูลส่วนตัวหรือข้อมูลลับที่ละเอียดอ่อน** โดยไม่มีการประเมินความเสี่ยง
- ❌ **ไม่ใช้แทนการตรวจสอบความปลอดภัยโดยผู้เชี่ยวชาญ** — ต้องมีการตรวจสอบโค้ดและความปลอดภัยตามปกติ
- ❌ **ไม่ใช้สำหรับระบบที่ต้องการความถูกต้อง 100% โดยไม่มีการตรวจสอบจากมนุษย์** — ตรวจสอบผลลัพธ์ทุกครั้งก่อนนำไปใช้งานจริง
- ❌ **ไม่ใช้เพื่อทดแทนความรู้และการตัดสินใจของผู้เชี่ยวชาญ** ในด้านกฎหมาย การเงิน หรือการแพทย์

---

## ⚠️ ข้อจำกัดและความเสี่ยงที่ต้องทราบ

### 🗣️ ภาษา
- ความสามารถและความถูกต้องอาจแตกต่างกันไปตามภาษาที่ใช้ — ภาษาอังกฤษมักได้รับการฝึกสอนมากกว่าภาษาอื่น

### 🧠 Hallucination (ข้อมูลเท็จ/สร้างขึ้น)
- AI อาจให้ข้อมูล คำอธิบาย หรือโค้ดที่ดูสมเหตุสมผลแต่ไม่ถูกต้อง
- ✅ **ตรวจสอบความถูกต้องทุกครั้งก่อนนำไปใช้งาน** โดยเฉพาะคำสั่งทางการเงิน ความปลอดภัย และข้อมูลทางกฎหมาย

### 🔒 ความปลอดภัยของโค้ด
- โค้ดที่แนะนำอาจมีจุดอ่อนด้านความปลอดภัย — ต้องผ่านการตรวจสอบตามมาตรฐานความปลอดภัยของทีมเสมอ
- อย่าให้ Copilot เข้าถึงข้อมูลลับ รหัสผ่าน หรือคีย์ API ของระบบโดยตรง

### 📄 โค้ดสาธารณะ
- คุณสมบัติ Public code matching อาจไม่ครอบคลุมทุกกรณี — ต้องตรวจสอบลิขสิทธิ์การใช้งานโค้ดที่ได้รับแนะนำด้วยตัวเอง

### 💻 CLI และคำสั่งระบบ
- คำสั่งที่แนะนำอาจแตกต่างกันไปตามระบบปฏิบัติและสภาพแวดล้อม — ทดสอบในสภาพแวดล้อมที่ปลอดภัยก่อนใช้งานจริง

### ⚖️ อคติและความไม่เท่าเทียมกัน
- เนื่องจากโมเดลเรียนรู้จากข้อมูลสาธารณะ อาจมีอคติที่มีอยู่ในข้อมูลปรากฏออกมาในผลลัพธ์
- หากพบรูปแบบที่ไม่ยุติธรรมหรือไม่เหมาะสม ให้แจ้งผ่านระบบรายงานปัญหาของ GitHub

---

## 🛡️ การป้องกันและความปลอดภัยในตัว

| มาตรการ | คำอธิบาย |
|---|---|
| � **Content filtering** | กรองเนื้อหาที่เป็นอันตรายหรือไม่เหมาะสมทั้งคำขอและคำตอบ |
| 📄 **Public code matching** | แจ้งเตือนเมื่อโค้ดที่แนะนำตรงกับโค้ดสาธารณะบน GitHub |
| 🧪 **Red teaming** | ทีมงานและผู้เชี่ยวชาญทดสอบหาจุดอ่อนก่อนเผยแพร่ทุกเวอร์ชัน |
| 👁️ **Human oversight** | มีช่องทางรายงานปัญหาและข้อผิดพลาดจากผู้ใช้เพื่อปรับปรุงระบบต่อไป |
| 🔁 **Feedback loop** | ข้อเสนอแนะและรายงานปัญหาถูกนำไปใช้ปรับปรุงความแม่นยำและความปลอดภัยของระบบ |

---

## 📋 แนวทางการใช้อย่างรับผิดชอบ (7 ข้อ)

1. ✅ **ตรวจสอบทุกครั้งก่อนนำไปใช้งาน** — ตรวจสอบโค้ด คำสั่ง และข้อมูลทุกครั้งก่อนนำไปใช้จริง
2. 🔒 **ไม่ส่งข้อมูลลับหรือข้อมูลส่วนตัว** — หลีกเลี่ยงการใส่รหัสผ่าน คีย์ API หรือข้อมูลที่ละเอียดอ่อนในกล่องสนทนา
3. 📚 **ทำความเข้าใจสิ่งที่ได้รับ** — ไม่ใช้สิ่งที่ไม่เข้าใจ ปรับแก้ให้เหมาะสมกับบริบทของโปรเจกต์
4. 🧪 **ทดสอบเสมอ** — ทดสอบโค้ดที่สร้างหรือแก้ไขโดย Copilot ในสภาพแวดล้อมที่ปลอดภัยก่อนส่งมอบ
5. 📖 **อ้างอิงแหล่งที่มา** — ตรวจสอบที่มาของโค้ดหากตรงกับโค้ดสาธารณะ และปฏิบัติตามใบอนุญาตที่เกี่ยวข้อง
6. ⚠️ **รายงานปัญหา** — แจ้งข้อผิดพลาด เนื้อหาที่ไม่เหมาะสม หรือพฤติกรรมที่ผิดปกติผ่านทาง GitHub
7. 🧑‍🤝‍🧑 **แบ่งปันความรู้และประสบการณ์** — แลกเปลี่ยนเทคนิคและข้อควรระวังกับสมาชิกในทีม

> 📝 **เพิ่มเติมสำหรับทีมงาน:**
> - 📝 บันทึกคำสั่งและบริบทสำคัญไว้ในโค้ดหรือเอกสาร — ไม่พึ่งพาเพียงการสนทนากับ Copilot
> - 🔄 ติดตามการเปลี่ยนแปลงนโยบายและความสามารถจาก GitHub อย่างสม่ำเสมอ
> - 🧑‍🤝‍🧑 แบ่งปันกรณีที่พบปัญหาหรือข้อผิดพลาดกับสมาชิกในทีมเพื่อเรียนรู้ร่วมกัน

---

## 🔗 แหล่งข้อมูลเพิ่มเติม

- 📖 **เอกสารทางการ GitHub Copilot:** https://docs.github.com/copilot
- 🧠 **Microsoft Responsible AI Standard:** https://www.microsoft.com/en-us/ai/responsible-ai
- 🔒 **นโยบายความเป็นส่วนตัว:** https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement
- ⚠️ **รายงานปัญหาและข้อเสนอแนะ:** ใช้ระบบ Feedback ภายในผลิตภัณฑ์หรือหน้า Community Forum ของ GitHub

---

> ✅ **ฉบับปรับปรุงเสร็จสมบูรณ์ — เวอร์ชัน 1.1.0 | 11 ตุลาคม 2026**
>
> ต้องการปรับแก้ส่วนใดเพิ่มเติมไหมครับ 😊

📄 คู่มือการใช้งาน GitHub Copilot Chat — เพิ่มส่วนเครื่องมือ
 
📅 เวอร์ชัน 1.2 | อัปเดตล่าสุด: 11 ตุลาคม 2026
 
 
 
🛠️ เครื่องมือและช่องทางการใช้งาน Copilot
 
💬 ช่องทางการใช้งานหลัก
 
เครื่องมือ/ช่องทาง คำอธิบาย สภาพแวดล้อมที่เหมาะสม 
Copilot Inline Suggestions คำแนะนำโค้ดแบบอัตโนมัติขณะพิมพ์ — ไม่ต้องเปิดแชท เขียนโค้ดต่อเนื่อง, โครงสร้างซ้ำๆ 
Copilot Chat ใน IDE แชทแบบเต็มรูปแบบภายใน VS Code / JetBrains — อ้างอิงไฟล์และโค้ดที่เลือกได้ อธิบายโค้ด, แก้ปัญหา, ปรับปรุงโค้ด, เขียนทดสอบ 
Copilot Chat ใน GitHub แชทบนหน้าเว็บ GitHub — ทำงานร่วมกับ PR, Issue, โค้ดออนไลน์ สนทนาเกี่ยวกับโปรเจกต์ร่วมกับทีม, ตรวจสอบ PR จากที่ใดก็ได้ 
Copilot Chat ใน GitHub Mobile ใช้งานผ่านแอปมือถือ — ตรวจสอบและถามคำถามได้ทุกที่ ตรวจสอบความคืบหน้า, อ่านคำอธิบาย PR, ถามคำถามด่วน 
Copilot CLI เรียกใช้ Copilot จากบรรทัดคำสั่งในเทอร์มินัล คำสั่ง Git, การจัดการไฟล์, สคริปต์, งานระบบ 
Copilot ใน Windows Terminal ผสานรวมกับเทอร์มินัล Windows — ช่วยเขียนและอธิบายคำสั่ง ผู้ใช้ Windows ที่ทำงานผ่านบรรทัดคำสั่งบ่อย 
Copilot ใน GitHub Desktop ผสานรวมในแอป GitHub Desktop — จัดการ Git พร้อมคำแนะนำ ผู้ใช้ GUI สำหรับ Git ที่ต้องการความช่วยเหลือเพิ่มเติม 
 
 
 
🚀 ความสามารถและฟีเจอร์พิเศษ
 
ฟีเจอร์ คำอธิบาย ประโยชน์ 
Pull Request Summaries สร้างสรุปคำอธิบาย PR อัตโนมัติจากการเปลี่ยนแปลงโค้ด ประหยัดเวลาเขียนคำอธิบาย PR ให้ครบถ้วนสม่ำเสมอ 
Commit Message Generation แนะนำข้อความ Commit ที่สื่อความหมายจากการเปลี่ยนแปลง มาตรฐานข้อความ Commit ทั้งทีม 
Code Review Assistance ช่วยตรวจสอบโค้ด — ค้นหาปัญหา แนะนำการปรับปรุง อธิบายตรรกะ เพิ่มความเร็วและคุณภาพการตรวจสอบโค้ด 
Copilot Coding Agent ผู้ช่วยที่ทำงานอัตโนมัติ — วางแผน, เขียน, แก้ไข, ทดสอบโค้ดแบบทีละขั้นตอน จัดการงานที่ซับซ้อนได้โดยละเอียดและมีขั้นตอน 
Spark คำแนะนำโค้ดที่รวดเร็วและกระชับ — เสนอการเปลี่ยนแปลงโดยไม่ต้องพิมพ์คำสั่งยาว รับคำแนะนำทันทีโดยไม่ต้องออกจากจอเขียนโค้ด 
Copilot Spaces พื้นที่ทำงานร่วมกัน — แชร์บริบท การสนทนา และผลลัพธ์กับสมาชิกในทีม ทีมทำงานบนฐานข้อมูลความรู้เดียวกัน ไม่ต้องอธิบายซ้ำ 
Agent Management จัดการเซสชัน, ตรวจสอบความคืบหน้า, สลับงานได้โดยไม่สูญเสียบริบท จัดการหลายงานได้อย่างเป็นระเบียบ 
Agent Skills ความสามารถเฉพาะด้าน — เขียนทดสอบ, ปรับโครงสร้าง, อธิบายสถาปัตยกรรม ฯลฯ Copilot เชี่ยวชาญงานแต่ละประเภทได้ดียิ่งขึ้น 
Agentic Memory จดจำสิ่งที่เรียนรู้เกี่ยวกับโปรเจกต์ — นำมาใช้ในการทำงานครั้งต่อไป ไม่ต้องอธิบายบริบทเดิมซ้ำๆ ในทุกครั้งที่เปิดเซสชันใหม่ 
Auto Model Selection เลือกโมเดลที่เหมาะสมกับประเภทงานโดยอัตโนมัติ ผลลัพธ์ดีที่สุดโดยไม่ต้องเลือกเอง 
Custom Agents สร้างผู้ช่วยเฉพาะงาน — กำหนดบทบาท กฎ และเครื่องมือที่ต้องการใช้เอง ปรับ Copilot ให้ตรงกับกระบวนการทำงานของทีมคุณ 
 
 
 
📋 ตารางเลือกใช้เครื่องมือให้เหมาะสม
 
สิ่งที่ต้องการทำ แนะนำเครื่องมือหลัก เครื่องมือรอง 
✍️ เขียนโค้ดใหม่อย่างรวดเร็ว Inline Suggestions Chat ใน IDE 
🤔 เข้าใจโค้ด/แก้ปัญหาที่ซับซ้อน Chat ใน IDE — 
📖 ตรวจสอบ/สนทนาเกี่ยวกับ Pull Request Chat ใน GitHub PR Summaries 
💻 ทำงานในเทอร์มินัล/เขียนสคริปต์ Copilot CLI — 
👥 ทำงานร่วมกับทีม แชร์ความเข้าใจ Copilot Spaces Chat ใน GitHub 
🤖 งานซับซ้อนที่ต้องทำทีละขั้นตอน Copilot Coding Agent — 
📝 เขียนคำอธิบาย PR / ข้อความ Commit PR Summaries / Commit Message Gen — 
🔍 ตรวจสอบคุณภาพโค้ดก่อนส่ง Code Review Chat ใน IDE 
📱 ตรวจสอบความคืบหน้าเมื่อไม่อยู่ที่โต๊ะ Chat ใน GitHub Mobile — 
 
 
 
⚡ เคล็ดลับ: ผสานหลายเครื่องมือเข้าด้วยกัน
 
ตัวอย่างเวิร์กโฟลว์ที่มีประสิทธิภาพ:
 
1. ✍️ ใช้ Inline Suggestions เขียนโค้ดเบื้องต้น
2. 🤖 ใช้ Coding Agent ช่วยจัดการงานที่ซับซ้อนและทดสอบ
3. 📝 ให้ PR Summaries สร้างร่างคำอธิบาย PR
4. 👥 สนทนาต่อใน Copilot Spaces เพื่อให้ทีมเข้าใจตรงกัน
5. 💻 ใช้ Copilot CLI รันคำสั่งและจัดการ Git ในเทอร์มินัล
 
 
 
💡 จำไว้: ไม่มีเครื่องมือเดียวที่ดีที่สุดสำหรับทุกงาน — เลือกเครื่องมือให้ตรงกับสิ่งที่กำลังทำอยู่ และผสานใช้งานเพื่อประสิทธิภาพสูงสุด ✅
 
 
 
ต้องการเพิ่มรายละเอียดสำหรับเครื่องมือใดเป็นพิเศษไหมครับ 😊