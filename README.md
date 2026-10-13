# runkksoAi 🤖

AI Assistant CLI ที่รันคำสั่ง bash ได้จริง — ทำงานบน **Termux**, Linux และ macOS

## ความสามารถ
- ✅ ตัวติดตั้งมีเมนู **เลือกภาษา 1, 2, 3, ... จนครบทุกภาษา** (ไทย, English, 日本語, 中文, Español, Français, Deutsch, Português, Русский, Indonesia, 한국어, Tiếng Việt, العربية, हिन्दी)
- ✅ เปิดใช้ครั้งแรกมี **หน้าต่างให้กรอก API Key** พร้อมเลือกผู้ให้บริการ: OpenAI, Groq, OpenRouter, Together AI, Google Gemini (OpenAI-compatible), Ollama (local), และ **custom URL อื่นๆ**
- ✅ AI **รันคำสั่ง bash ได้จริง** บนเครื่องคุณ (ผ่าน function calling)
- ✅ คำสั่งที่ **ลบไฟล์** (`rm`, `rmdir`, `unlink`, `shred`, `find -delete`, `truncate` ฯลฯ) จะ **ถามยืนยันทุกครั้ง — ไม่มีข้อยกเว้น**
- ✅ คำสั่งแบบพังทั้งเครื่อง (`rm -rf /`, `mkfs`, `dd of=/dev/...`) จะ **ถูกปฏิเสธทันที**
- ✅ API Key เก็บใน `~/.runkksoai/config.json` ด้วยสิทธิ์ 0600 ไม่ถูกส่งไปไหนอื่น

## ติดตั้งบน Termux

```bash
pkg update && pkg install git python -y
git clone <repo-url> runkksoAi
cd runkksoAi
bash install.sh      # เลือกภาษา 1,2,3,... แล้วติดตั้งอัตโนมัติ
```

เสร็จแล้วพิมพ์:

```bash
runkksoai            # ครั้งแรกจะขึ้นหน้าต่างให้กรอก API Key
```

## การใช้งานในแชท

```
[คุณ] > ในโฟลเดอร์นี้มีไฟล์อะไรบ้าง
  ⚡ $ ls -la
[AI] มีไฟล์ ... 

[คุณ] > ลบไฟล์ old.log ที
  🗑  mode: delete — rm old.log
⚠️  คำสั่งนี้จะ **ลบไฟล์** — ยืนยันการลบ? (y/n): y
  ⚡ $ rm old.log
```

คำสั่งในแชท: `/exit` ออก • `/new` คุยใหม่ • `/setup` ตั้งค่า API • `/lang` เปลี่ยนภาษา • `/help`

ออปชัน: `--setup` (เปิดหน้าต่างตั้งค่าใหม่), `--lang th` (ระบุภาษา), `echo "hi" | runkksoai` (โหมด pipe)

## โครงสร้างไฟล์
```
runkksoAi/
├── install.sh     # ตัวติดตั้ง เลือกภาษา 1,2,3,... (Termux/Linux/macOS)
├── runkksoai.py   # ตัว AI CLI หลัก (Python stdlib เท่านั้น ไม่ต้อง pip)
└── README.md
```

## ผู้พัฒนา 👨‍💻
- **Roblox:** https://www.roblox.com/en/users/5509501038/profile
- **YouTube:** https://youtube.com/@kkso882?si=4AfUoiWQ4fUVXcUU
