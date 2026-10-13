#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
runkksoAi — AI Assistant CLI
รองรับ Termux / Linux / macOS • รองรับทุก API แบบ OpenAI-compatible
AI รันคำสั่ง bash ได้ | คำสั่งที่ลบไฟล์จะถามยืนยันทุกครั้ง

ผู้พัฒนา:
  Roblox  : https://www.roblox.com/en/users/5509501038/profile
  YouTube : https://youtube.com/@kkso882?si=4AfUoiWQ4fUVXcUU
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

try:  # Termux/เครื่องเก่าๆ บางที encoding เพี้ยน
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ทดสอบสามารถ redirect ที่เก็บ config ได้ เพื่อไม่ไปทับ config จริงของผู้ใช้
CONFIG_DIR = os.environ.get("RUNKKSOAI_CONFIG_DIR") or os.path.join(
    os.path.expanduser("~"), ".runkksoai")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

URL_ROBLOX = "https://www.roblox.com/en/users/5509501038/profile"
URL_YOUTUBE = "https://youtube.com/@kkso882?si=4AfUoiWQ4fUVXcUU"


def make_banner() -> str:
    """แบนเนอร์ + เครดิตผู้พัฒนา แสดงตอนเปิดโปรแกรม"""
    links = [f"Roblox : {URL_ROBLOX}", f"YouTube: {URL_YOUTUBE}"]
    lines = [
        "╔══════════════════════════════════════════════════════╗",
        f"║   runkksoAi — AI Assistant CLI                       ║",
        "╠══════════════════════════════════════════════════════╣",
    ]
    for ln in links:
        pad = ln + " " * max(0, 52 - len(ln))
        lines.append(f"║ {pad} ║")
    lines.append("╚══════════════════════════════════════════════════════╝")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────
#                                                           i18n
# ─────────────────────────────────────────────────────────────
I18N = {
    "th": {
        "choose_provider": "เลือกผู้ให้บริการ API:",
        "enter_key": "กรอก API Key:",
        "custom_base": "กรอก Base URL (เช่น https://api.example.com/v1):",
        "model_prompt": "กรอกชื่อโมเดล [{d}]:",
        "saved": "✔ บันทึกการตั้งค่าแล้วที่ {path}",
        "confirm_delete": "⚠️  คำสั่งนี้จะ **ลบไฟล์** — ยืนยันการลบ? (y/n): ",
        "blocked": "🚫 คำสั่งอันตรายเกินไป จึงห้ามรัน",
        "denied": "ถูกยกเลิกโดยผู้ใช้ (ผู้ใช้ปฏิเสธการรันคำสั่งนี้)",
        "you": "คุณ",
        "ai": "AI",
        "exit_msg": "ลาก่อน! 👋",
        "setup_hint": "แก้การตั้งค่า: runkksoai --setup • เปลี่ยนภาษา: --lang th",
        "http401": "API Key ไม่ถูกต้อง (401) — ใช้ runkksoai --setup เพื่อกรอกใหม่",
        "error": "เกิดข้อผิดพลาด: {err}",
        "ask_all": "รันคำสั่งนี้หรือไม่? (y/n): ",
        "help": "คำสั่ง: /exit ออก • /new คุยใหม่ • /setup ตั้งค่า • /lang เปลี่ยนภาษา • /help",
    },
    "en": {
        "choose_provider": "Choose an API provider:",
        "enter_key": "Enter API key:",
        "custom_base": "Enter base URL (e.g. https://api.example.com/v1):",
        "model_prompt": "Enter model [{d}]:",
        "saved": "✔ Settings saved to {path}",
        "confirm_delete": "⚠️  This command **deletes files** — confirm? (y/n): ",
        "blocked": "🚫 Command too dangerous, refused.",
        "denied": "Denied by user (the user rejected this command).",
        "you": "You",
        "ai": "AI",
        "exit_msg": "Bye! 👋",
        "setup_hint": "Settings: runkksoai --setup • language: --lang en",
        "http401": "Invalid API key (401) — run `runkksoai --setup` to re-enter.",
        "error": "Error: {err}",
        "ask_all": "Run this command? (y/n): ",
        "help": "Commands: /exit quit • /new reset • /setup settings • /lang language • /help",
    },
    "ja": {
        "choose_provider": "APIプロバイダーを選択:",
        "enter_key": "APIキーを入力:",
        "custom_base": "Base URL を入力:",
        "model_prompt": "モデル名 [{d}]:",
        "saved": "✔ 設定を保存しました: {path}",
        "confirm_delete": "⚠️  このコマンドは**ファイルを削除**します — 実行しますか？ (y/n): ",
        "blocked": "🚫 危険すぎるため拒否しました。",
        "denied": "ユーザーがこのコマンドを拒否しました。",
        "you": "あなた",
        "ai": "AI",
        "exit_msg": "またね！ 👋",
        "setup_hint": "設定: runkksoai --setup • 言語: --lang ja",
        "http401": "APIキーが無効です (401) — `runkksoai --setup` で再設定してください。",
        "error": "エラー: {err}",
        "ask_all": "このコマンドを実行しますか？ (y/n): ",
        "help": "コマンド: /exit 終了 • /new リセット • /setup 設定 • /lang 言語 • /help",
    },
    "zh": {
        "choose_provider": "选择 API 服务商:",
        "enter_key": "输入 API Key:",
        "custom_base": "输入 Base URL:",
        "model_prompt": "输入模型名 [{d}]:",
        "saved": "✔ 已保存配置: {path}",
        "confirm_delete": "⚠️  该命令将**删除文件** — 确认执行？ (y/n): ",
        "blocked": "🚫 命令太危险，已拒绝。",
        "denied": "用户拒绝了此命令。",
        "you": "你",
        "ai": "AI",
        "exit_msg": "再见！ 👋",
        "setup_hint": "设置: runkksoai --setup • 语言: --lang zh",
        "http401": "API Key 无效 (401) — 请运行 `runkksoai --setup` 重新设置。",
        "error": "错误: {err}",
        "ask_all": "要运行这个命令吗？ (y/n): ",
        "help": "命令: /exit 退出 • /new 重置 • /setup 设置 • /lang 语言 • /help",
    },
    "es": {
        "choose_provider": "Elija el proveedor de API:",
        "enter_key": "Introduzca API Key:",
        "custom_base": "Introduzca Base URL:",
        "model_prompt": "Modelo [{d}]:",
        "saved": "✔ Configuración guardada en {path}",
        "confirm_delete": "⚠️  Este comando **borra archivos** — ¿confirmar? (y/n): ",
        "blocked": "🚫 Comando demasiado peligroso, rechazado.",
        "denied": "Denegado por el usuario.",
        "you": "Tú",
        "ai": "IA",
        "exit_msg": "¡Adiós! 👋",
        "setup_hint": "Config: runkksoai --setup • idioma: --lang es",
        "http401": "API Key inválida (401) — ejecute `runkksoai --setup`.",
        "error": "Error: {err}",
        "ask_all": "¿Ejecutar este comando? (y/n): ",
        "help": "Comandos: /exit salir • /new nuevo • /setup config • /lang idioma • /help",
    },
    "fr": {
        "choose_provider": "Choisissez le fournisseur API :",
        "enter_key": "Entrez la clé API :",
        "custom_base": "Entrez l'URL de base :",
        "model_prompt": "Modèle [{d}] :",
        "saved": "✔ Réglages enregistrés dans {path}",
        "confirm_delete": "⚠️  Cette commande **supprime des fichiers** — confirmez ? (o/n) : ",
        "blocked": "🚫 Commande trop dangereuse, refusée.",
        "denied": "Refusé par l'utilisateur.",
        "you": "Vous",
        "ai": "IA",
        "exit_msg": "Au revoir ! 👋",
        "setup_hint": "Réglages : runkksoai --setup • langue : --lang fr",
        "http401": "Clé API invalide (401) — lancez `runkksoai --setup`.",
        "error": "Erreur : {err}",
        "ask_all": "Exécuter cette commande ? (o/n) : ",
        "help": "Commandes : /exit quitter • /new recommencer • /setup réglages • /lang langue • /help",
    },
    "de": {
        "choose_provider": "API-Anbieter wählen:",
        "enter_key": "API-Key eingeben:",
        "custom_base": "Base-URL eingeben:",
        "model_prompt": "Modell [{d}]:",
        "saved": "✔ Einstellungen gespeichert in {path}",
        "confirm_delete": "⚠️  Dieser Befehl **löscht Dateien** — bestätigen? (j/n): ",
        "blocked": "🚫 Befehl zu gefährlich, abgelehnt.",
        "denied": "Vom Benutzer abgelehnt.",
        "you": "Du",
        "ai": "KI",
        "exit_msg": "Tschüss! 👋",
        "setup_hint": "Einstellungen: runkksoai --setup • Sprache: --lang de",
        "http401": "Ungültiger API-Key (401) — `runkksoai --setup` ausführen.",
        "error": "Fehler: {err}",
        "ask_all": "Diesen Befehl ausführen? (j/n): ",
        "help": "Befehle: /exit beenden • /new zurücksetzen • /setup Einstellungen • /lang Sprache • /help",
    },
    "pt": {
        "choose_provider": "Escolha o provedor de API:",
        "enter_key": "Digite a API Key:",
        "custom_base": "Digite a Base URL:",
        "model_prompt": "Modelo [{d}]:",
        "saved": "✔ Configuração salva em {path}",
        "confirm_delete": "⚠️  Este comando **apaga arquivos** — confirmar? (s/n): ",
        "blocked": "🚫 Comando muito perigoso, recusado.",
        "denied": "Recusado pelo usuário.",
        "you": "Você",
        "ai": "IA",
        "exit_msg": "Tchau! 👋",
        "setup_hint": "Config: runkksoai --setup • idioma: --lang pt",
        "http401": "API Key inválida (401) — execute `runkksoai --setup`.",
        "error": "Erro: {err}",
        "ask_all": "Executar este comando? (s/n): ",
        "help": "Comandos: /exit sair • /new reiniciar • /setup config • /lang idioma • /help",
    },
    "ru": {
        "choose_provider": "Выберите провайдера API:",
        "enter_key": "Введите API-ключ:",
        "custom_base": "Введите Base URL:",
        "model_prompt": "Модель [{d}]:",
        "saved": "✔ Настройки сохранены: {path}",
        "confirm_delete": "⚠️  Команда **удаляет файлы** — подтвердить? (y/n): ",
        "blocked": "🚫 Команда слишком опасна, отказано.",
        "denied": "Отклонено пользователем.",
        "you": "Вы",
        "ai": "ИИ",
        "exit_msg": "Пока! 👋",
        "setup_hint": "Настройки: runkksoai --setup • язык: --lang ru",
        "http401": "Неверный API-ключ (401) — выполните `runkksoai --setup`.",
        "error": "Ошибка: {err}",
        "ask_all": "Выполнить эту команду? (y/n): ",
        "help": "Команды: /exit выход • /new сброс • /setup настройки • /lang язык • /help",
    },
    "id": {
        "choose_provider": "Pilih penyedia API:",
        "enter_key": "Masukkan API Key:",
        "custom_base": "Masukkan Base URL:",
        "model_prompt": "Model [{d}]:",
        "saved": "✔ Pengaturan disimpan di {path}",
        "confirm_delete": "⚠️  Perintah ini **menghapus file** — konfirmasi? (y/n): ",
        "blocked": "🚫 Perintah terlalu berbahaya, ditolak.",
        "denied": "Ditolak oleh pengguna.",
        "you": "Anda",
        "ai": "AI",
        "exit_msg": "Sampai jumpa! 👋",
        "setup_hint": "Pengaturan: runkksoai --setup • bahasa: --lang id",
        "http401": "API Key salah (401) — jalankan `runkksoai --setup`.",
        "error": "Kesalahan: {err}",
        "ask_all": "Jalankan perintah ini? (y/n): ",
        "help": "Perintah: /exit keluar • /new mulai ulang • /setup pengaturan • /lang bahasa • /help",
    },
    "ko": {
        "choose_provider": "API 제공자 선택:",
        "enter_key": "API 키 입력:",
        "custom_base": "Base URL 입력:",
        "model_prompt": "모델 [{d}]:",
        "saved": "✔ 설정 저장됨: {path}",
        "confirm_delete": "⚠️  이 명령은 **파일을 삭제**합니다 — 실행할까요? (y/n): ",
        "blocked": "🚫 너무 위험한 명령이라 거부했습니다.",
        "denied": "사용자가 이 명령을 거부했습니다.",
        "you": "당신",
        "ai": "AI",
        "exit_msg": "안녕! 👋",
        "setup_hint": "설정: runkksoai --setup • 언어: --lang ko",
        "http401": "API 키가 잘못됐습니다 (401) — `runkksoai --setup` 실행.",
        "error": "오류: {err}",
        "ask_all": "이 명령을 실행할까요? (y/n): ",
        "help": "명령: /exit 종료 • /new 초기화 • /setup 설정 • /lang 언어 • /help",
    },
    "vi": {
        "choose_provider": "Chọn nhà cung cấp API:",
        "enter_key": "Nhập API Key:",
        "custom_base": "Nhập Base URL:",
        "model_prompt": "Mô hình [{d}]:",
        "saved": "✔ Đã lưu cấu hình tại {path}",
        "confirm_delete": "⚠️  Lệnh này sẽ **xóa tệp** — xác nhận? (y/n): ",
        "blocked": "🚫 Lệnh quá nguy hiểm, bị từ chối.",
        "denied": "Người dùng đã từ chối lệnh này.",
        "you": "Bạn",
        "ai": "AI",
        "exit_msg": "Tạm biệt! 👋",
        "setup_hint": "Cấu hình: runkksoai --setup • ngôn ngữ: --lang vi",
        "http401": "API Key sai (401) — chạy `runkksoai --setup`.",
        "error": "Lỗi: {err}",
        "ask_all": "Chạy lệnh này? (y/n): ",
        "help": "Lệnh: /exit thoát • /new đặt lại • /setup cấu hình • /lang ngôn ngữ • /help",
    },
    "ar": {
        "choose_provider": "اختر مزود API:",
        "enter_key": "أدخل مفتاح API:",
        "custom_base": "أدخل Base URL:",
        "model_prompt": "النموذج [{d}]:",
        "saved": "✔ تم حفظ الإعدادات في {path}",
        "confirm_delete": "⚠️  هذا الأمر **يحذف ملفات** — تأكيد؟ (y/n): ",
        "blocked": "🚫 أمر خطير جدًا، تم الرفض.",
        "denied": "رفض المستخدم هذا الأمر.",
        "you": "أنت",
        "ai": "الذكاء الاصطناعي",
        "exit_msg": "إلى اللقاء! 👋",
        "setup_hint": "الإعدادات: runkksoai --setup • اللغة: --lang ar",
        "http401": "مفتاح API غير صالح (401) — شغّل `runkksoai --setup`.",
        "error": "خطأ: {err}",
        "ask_all": "تنفيذ هذا الأمر؟ (y/n): ",
        "help": "أوامر: /exit خروج • /new جديد • /setup إعدادات • /lang لغة • /help",
    },
    "hi": {
        "choose_provider": "API प्रदाता चुनें:",
        "enter_key": "API Key दर्ज करें:",
        "custom_base": "Base URL दर्ज करें:",
        "model_prompt": "मॉडल [{d}]:",
        "saved": "✔ सेटिंग्स सहेजी गईं: {path}",
        "confirm_delete": "⚠️  यह कमांड **फाइलें डिलीट** करेगा — पुष्टि करें? (y/n): ",
        "blocked": "🚫 कमांड बहुत खतरनाक है, रद्द किया गया।",
        "denied": "उपयोगकर्ता ने इस कमांड को अस्वीकार किया।",
        "you": "आप",
        "ai": "AI",
        "exit_msg": "अलविदा! 👋",
        "setup_hint": "सेटिंग: runkksoai --setup • भाषा: --lang hi",
        "http401": "API Key गलत है (401) — `runkksoai --setup` चलाएं।",
        "error": "त्रुटि: {err}",
        "ask_all": "यह कमांड चलाएं? (y/n): ",
        "help": "कमांड: /exit बाहर • /new रीसेट • /setup सेटिंग • /lang भाषा • /help",
    },
}


def t(lang: str, key: str, **kw) -> str:
    lang_msgs = I18N.get(lang, I18N["en"])
    msg = lang_msgs.get(key, I18N["en"].get(key, key))
    return msg.format(**kw) if kw else msg


SUPPORTED_LANGS = list(I18N.keys())

# ─────────────────────────────────────────────────────────────
#  ผู้ให้บริการที่รองรับ (ทุกตัวใช้ protocol แบบ OpenAI-compatible)
# ─────────────────────────────────────────────────────────────
# (ชื่อ, base_url ค่าเริ่มต้น, โมเดลค่าเริ่มต้น, ต้องมี key ไหม)
PROVIDERS = [
    ("OpenAI", "https://api.openai.com/v1", "gpt-4o-mini", True),
    ("Groq", "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile", True),
    ("OpenRouter", "https://openrouter.ai/api/v1", "openai/gpt-4o-mini", True),
    ("Together AI", "https://api.together.xyz/v1", "meta-llama/Llama-3.3-70B-Instruct-Turbo", True),
    ("Google Gemini (OpenAI-compatible)", "https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-flash-lite-latest", True),
    ("Ollama (local, no key)", "http://localhost:11434/v1", "llama3.2", False),
    ("อื่นๆ — custom OpenAI-compatible", "", "", True),
]

# ─────────────────────────────────────────────────────────────
#  safety — ตรวจจับคำสั่งลบไฟล์ + คำสั่งอันตราย
# ─────────────────────────────────────────────────────────────
DELETE_RE = [
    re.compile(r"(?:^|[\s;&|(])rm(?:\.(?:exe|EXE))?(?:\s|$)"),
    re.compile(r"\brmdir\b"),
    re.compile(r"\bunlink\s"),
    re.compile(r"\bshred\s"),
    re.compile(r"\bfind\s[^;&|]*\s-delete\b"),
    re.compile(r"\btruncate\s+-s\s*0\b"),
    re.compile(r"\bmv\s+\S+\s+/dev/null\b"),
]
# คำสั่งแบบนี้ห้ามข้ามการยืนยันเด็ดขาด และคำสั่งที่พังทั้งเครื่องจะปฏิเสธทันที
CATASTROPHIC_RE = [
    re.compile(r"\brm\s+-[a-zA-Z]*[rf][a-zA-Z]*\s+(?:/\s*$|/\*)"),
    re.compile(r"\bmkfs(?:\.\w+)?\b"),
    re.compile(r"\bdd\b[^\n]*of=/dev/(?:sd|nvme|mmcblk|hd)"),
    re.compile(r":\(\)\s*\{.*\};\s*:"),
    re.compile(r"chmod\s+-R\s+\d+\s+/(?:\s|$)"),
]


def classify_command(cmd: str):
    """return (allowed_to_ask, reason)
    - catastrophic → (False, blocked)
    - delete command → (True, must_confirm)
    - อื่นๆ → (True, normal)
    """
    for rx in CATASTROPHIC_RE:
        if rx.search(cmd):
            return False, "blocked"
    for rx in DELETE_RE:
        if rx.search(cmd):
            return True, "must_confirm"
    return True, "normal"


def run_bash(command: str, timeout: int = 120):
    r = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=timeout,
        cwd=os.getcwd(),
    )
    out = (r.stdout or "") + ((("\n" + r.stderr) if r.stderr else ""))
    out = out.strip()
    if len(out) > 8000:
        out = out[:8000] + f"\n...[truncated, total {len(out)} chars, exit={r.returncode}]"
    return out or f"(no output, exit={r.returncode})"


# ─────────────────────────────────────────────────────────────
#  tools schema สำหรับ function calling แบบ OpenAI
# ─────────────────────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": (
                "Run a bash command on the user's machine and return its output. "
                "Use it to inspect files, install things, build, and to *exactly* execute "
                "what the user asked. IMPORTANT: commands that delete files (rm/rmdir/unlink/"
                "shred/find -delete) will ask the user for confirmation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The bash command to run"},
                },
                "required": ["command"],
            },
        },
    }
]

SYSTEM_PROMPT = (
    "You are runkksoAi, a helpful CLI AI assistant living in the user's terminal "
    "(Termux/Linux/macOS). You can execute bash commands with the run_bash tool to help "
    "the user. Prefer safe, read-only commands (ls, cat, grep...) before destructive ones. "
    "Never delete anything unless the user clearly asked for it. Answer in the same "
    "language the user uses. Be concise."
)

# ─────────────────────────────────────────────────────────────
#  config
# ─────────────────────────────────────────────────────────────
def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(cfg: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    try:  # ป้องกันคนอื่นอ่าน key
        os.chmod(CONFIG_PATH, 0o600)
    except Exception:
        pass


def setup_wizard(lang: str):
    print()
    print("┌─────────────────────────────── SETUP ───────────────────────────────┐")
    print(t(lang, "choose_provider"))
    for i, (name, _, _, _) in enumerate(PROVIDERS, start=1):
        print(f"  {i}) {name}")
    while True:
        choice = input("  > ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(PROVIDERS):
            break
        print(f"  ✗ 1-{len(PROVIDERS)}")
    name, base_url, model, need_key = PROVIDERS[int(choice) - 1]

    is_custom = choice == str(len(PROVIDERS))
    if is_custom:
        while not base_url.strip():
            base_url = input(t(lang, "custom_base") + " ").strip()
    if is_custom:
        while not model.strip():
            model = input(t(lang, "model_prompt", d="(required)") + " ").strip()
    else:
        typed = input(t(lang, "model_prompt", d=model) + " ").strip()
        model = typed or model  # กด Enter เพื่อใช้ค่าเริ่มต้นของผู้ให้บริการ

    api_key = ""
    if need_key:
        # ใช้ input ธรรมดา — getpass มักค้าง/มองไม่เห็นการพิมพ์บน Termux มือถือ
        # key จะแสดงข้อความตอนพิมพ์ จึงพิมพ์/แก้ไขได้ และถูกเก็บลงไฟล์สิทธิ์ 0600
        while not api_key.strip():
            api_key = input(t(lang, "enter_key") + " ").strip()
            if not api_key:
                print("  ✗ (ส่วนนี้ต้องกรอก) ลองพิมพ์ใหม่ / try again")

    lang_in = ""
    while lang_in not in I18N:
        lang_in = input(f"  language/Language ({', '.join(SUPPORTED_LANGS)}) [{lang}]: ").strip() or lang

    cfg = {
        "provider": name,
        "base_url": base_url.rstrip("/"),
        "model": model,
        "api_key": api_key,
        "lang": lang_in,
    }
    save_config(cfg)
    print(t(lang_in, "saved", path=CONFIG_PATH))
    print()
    return cfg


# ─────────────────────────────────────────────────────────────
#  API call (OpenAI-compatible chat completions)
# ─────────────────────────────────────────────────────────────
def api_chat(cfg: dict, messages: list) -> dict:
    base = cfg["base_url"].rstrip("/")
    url = base + "/chat/completions"
    body = {"model": cfg["model"], "messages": messages, "tools": TOOLS, "tool_choice": "auto"}
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if cfg.get("api_key"):
        headers["Authorization"] = "Bearer " + cfg["api_key"]
    if "openrouter" in base:
        headers["HTTP-Referer"] = "https://github.com/runkksoAi"
        headers["X-Title"] = "runkksoAi"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    import time
    last_err = None
    for attempt in range(4):  # auto-retry: provider ฟรีมัก 503/429 ชั่วขณะ
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:300]
            if e.code == 401:
                raise RuntimeError("HTTP401:" + detail) from e
            if e.code in (429, 500, 503) and attempt < 3:
                last_err = f"HTTP {e.code}: {detail}"
                time.sleep(1.5 * (attempt + 1) * (attempt + 1))
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}") from e


def get_tool_calls(resp: dict):
    try:
        msg = resp["choices"][0]["message"]
    except (KeyError, IndexError):
        return None, ""
    calls = msg.get("tool_calls") or []
    return calls, msg.get("content") or ""


# ─────────────────────────────────────────────────────────────
#  chat loop
# ─────────────────────────────────────────────────────────────
def execute_tool_call(cfg: dict, lang: str, call: dict) -> str:
    fn = call.get("function", {})
    name = fn.get("name", "")
    try:
        args = json.loads(fn.get("arguments") or "{}")
    except json.JSONDecodeError:
        args = {}

    if name != "run_bash":
        return f"unknown tool: {name}"

    command = (args.get("command") or "").strip()
    if not command:
        user_answer = "n"
    allowed, reason = classify_command(command)
    if not allowed:
        print(t(lang, "blocked"))
        return f"REFUSED: {t(lang, 'blocked')}\ncommand: {command}"

    if reason == "must_confirm":  # ← ลบไฟล์: ถามทุกครั้ง ไม่มีข้อยกเว้น
        print(f"\n  🗑  mode: delete — {command}")
        user_answer = input(t(lang, "confirm_delete")).strip().lower()
    else:
        user_answer = "y"

    if user_answer not in ("y", "yes"):
        print("  ✗ canceled")
        return t(lang, "denied") + f"\n(command: {command})"

    print(f"  ⚡ $ {command}")
    try:
        return run_bash(command)
    except subprocess.TimeoutExpired:
        return "ERROR: command timed out (120s)"
    except Exception as e:  # noqa: BLE001
        return f"ERROR: {e}"


def chat_loop(cfg: dict):
    lang = cfg.get("lang", "en")
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print(t(lang, "setup_hint"))
    print(t(lang, "help"))
    print()

    while True:
        try:
            user = input(f"\033[1;32m[{t(lang, 'you')}]\033[0m > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue

        low = user.lower()
        if low in ("/exit", "/quit", "exit", "quit"):
            print(t(lang, "exit_msg"))
            break
        if low == "/new":
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("  ↺ new session")
            continue
        if low == "/setup":
            cfg = setup_wizard(lang)
            lang = cfg.get("lang", lang)
            print(t(lang, "help"))
            continue
        if low == "/lang":
            for i, lc in enumerate(SUPPORTED_LANGS, 1):
                print(f"  {i}) {lc}")
            choice = input("  > ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(SUPPORTED_LANGS):
                lang = SUPPORTED_LANGS[int(choice) - 1]
                cfg["lang"] = lang
                save_config(cfg)
            continue
        if low == "/help":
            print(t(lang, "help"))
            continue

        history.append({"role": "user", "content": user})

        # ── loop: model can call tools repeatedly until final answer ──
        try:
            for _ in range(15):  # hard cap ต่อ turn
                resp = api_chat(cfg, history)
                calls, content = get_tool_calls(resp)

                if content:
                    print(f"\033[1;36m[{t(lang, 'ai')}]\033[0m {content}")
                    history.append({"role": "assistant", "content": content,
                                    **({"tool_calls": calls} if calls else {})})
                elif calls:
                    history.append({"role": "assistant",
                                    "content": None,
                                    "tool_calls": calls})
                else:
                    history.append({"role": "assistant", "content": ""})
                    break

                if not calls:
                    break

                for call in calls:
                    result = execute_tool_call(cfg, lang, call)
                    history.append({
                        "role": "tool",
                        "tool_call_id": call.get("id", ""),
                        "content": result,
                    })
        except RuntimeError as e:
            msg = str(e)
            if msg.startswith("HTTP401"):
                print(f"\033[1;31m{t(lang, 'http401')}\033[0m")
                break
            print(f"\033[1;31m{t(lang, 'error', err=msg)}\033[0m")
        except urllib.error.URLError as e:
            print(f"\033[1;31m{t(lang, 'error', err=str(e.reason))}\033[0m")
        finally:
            history = history[:400]


# ─────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    help_only = {"-h", "--help"}
    if any(a in help_only for a in args):
        print(make_banner())
        print("usage: runkksoai [--setup] [--lang <code>]")
        print("on first run a setup window asks for the API key.")
        return 0
    if any(a == "--credit" for a in args):
        print(make_banner())
        return 0

    cfg = load_config()
    # --lang XX เขียนทับภาษาใน config
    if "--lang" in args:
        i = args.index("--lang")
        if i + 1 < len(args) and args[i + 1] in I18N:
            cfg["lang"] = args[i + 1]
            if cfg.get("base_url"):
                save_config(cfg)

    # first run → หน้าต่างตั้งค่าให้กรอก API key
    if "--setup" in args or not cfg.get("base_url") or not cfg.get("model"):
        cfg = setup_wizard(cfg.get("lang", "en"))

    print(make_banner())
    if sys.stdin.isatty():
        chat_loop(cfg)
    else:  # pipe mode เช่น echo "hi" | runkksoai
        user = sys.stdin.read().strip()
        if user:
            history = [{"role": "system", "content": SYSTEM_PROMPT},
                       {"role": "user", "content": user}]
            lang = cfg.get("lang", "en")
            try:
                for _ in range(8):  # วนจน AI ตอบข้อความสุดท้าย (เหมือน interactive)
                    resp = api_chat(cfg, history)
                    calls, content = get_tool_calls(resp)
                    if content:
                        print(content)
                    if not calls:
                        break
                    history.append({"role": "assistant", "content": content or None,
                                    "tool_calls": calls})
                    for call in calls:
                        result = execute_tool_call(cfg, lang, call)
                        print(f"--- tool result ---\n{result}")
                        history.append({"role": "tool",
                                        "tool_call_id": call.get("id", ""),
                                        "content": result})
            except RuntimeError as e:
                msg = str(e)
                if msg.startswith("HTTP401"):
                    print(t(cfg.get("lang", "en"), "http401"))
                    return 1
                print(t(cfg.get("lang", "en"), "error", err=msg))
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
