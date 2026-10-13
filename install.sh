#!/usr/bin/env bash
# runkksoAi installer — เมนูเลือกภาษา 1,2,3,... รองรับ Termux / Linux / macOS
# ผู้พัฒนา: https://www.roblox.com/en/users/5509501038/profile
#           https://youtube.com/@kkso882?si=4AfUoiWQ4fUVXcUU
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

C1='\033[1;36m'; C2='\033[1;33m'; C0='\033[0m'
echo ""
printf "${C1}██╗ running \`runkksoAi\` installer${C0}\n"
printf "${C1}╔════════════════════════════════════════╗${C0}\n"
printf "${C1}║   runkksoAi  •  AI Assistant CLI       ║${C0}\n"
printf "${C1}║   Dev: Roblox 5509501038 / yt @kkso882 ║${C0}\n"
printf "${C1}╚════════════════════════════════════════╝${C0}\n"
printf "${C2}  Roblox : https://www.roblox.com/en/users/5509501038/profile${C0}\n"
printf "${C2}  YouTube: https://youtube.com/@kkso882${C0}\n"
echo ""

# ---------- ตรวจว่าเป็น Termux / Linux / macOS ----------
IS_TERMUX=0
case "${PREFIX:-}" in
  *com.termux*) IS_TERMUX=1 ;;
esac
if [ "$IS_TERMUX" -eq 0 ]; then
  case "$(uname -s)" in
    Linux|Darwin) ;;
    *)
      echo "⚠️  Unsupported OS: $(uname -s) (termux / linux / macos only)"
      exit 1 ;;
  esac
fi

# ---------- เมนูลิสต์ภาษา (แสดงชื่อภาษาแบบภาษาแม่) ----------
LANG_CODES=(th en ja zh es fr de pt ru id ko vi ar hi)
LANG_NAMES=("ไทย" "English" "日本語" "中文" "Español" "Français" "Deutsch" "Português" "Русский" "Bahasa Indonesia" "한국어" "Tiếng Việt" "العربية" "हिन्दी")

pick_language() {
  while true; do
    echo "══════════════════════════════════════"
    echo "  choose your language / เลือกภาษา 1,2,3,..."
    echo "══════════════════════════════════════"
    i=1
    for n in "${LANG_NAMES[@]}"; do
      echo "  ${i}) ${n}"
      i=$((i+1))
    done
    printf "  > "
    read -r CHOICE
    case "$CHOICE" in
      ''|*[!0-9]*) echo "  ✗ number only (1-14)"; continue ;;
    esac
    if [ "$CHOICE" -ge 1 ] 2>/dev/null && [ "$CHOICE" -le "${#LANG_CODES[@]}" ]; then
      LANG_IDX="$((CHOICE-1))"
      LANG_CODE="${LANG_CODES[$LANG_IDX]}"
      LANG_NAME="${LANG_NAMES[$LANG_IDX]}"
      break
    fi
    echo "  ✗ number only (1-${#LANG_CODES[@]})"
  done
}

pick_language
echo ""
echo "  ✓ $LANG_NAME selected"

# ---------- ข้อความแปลตามภาษาที่เลือก (fallback = English) ----------
localized() {
  case "$1" in
    th) echo "กำลังติดตั้ง...|ติดตั้งเรียบร้อย! พิมพ์ runkksoai เพื่อเริ่มใช้งาน (ครั้งแรกจะให้กรอก API Key)|รันด้วยคำสั่ง: runkksoai" ;;
    en) echo "Installing...|Installed! Type runkksoai to start (api key asked on first run)|Run command: runkksoai" ;;
    ja) echo "インストール中...|インストール完了！ runkksoai と入力して開始 (初回にAPIキーを入力)|実行コマンド: runkksoai" ;;
    zh) echo "正在安装...|安装完成！输入 runkksoai 开始 (首次运行会要求填写 API Key)|运行命令: runkksoai" ;;
    es) echo "Instalando...|¡Instalado! Escribe runkksoai para empezar (clave API al primer uso)|Comando: runkksoai" ;;
    fr) echo "Installation...|Installé ! Tapez runkksoai pour démarrer (clé API au premier lancement)|Commande : runkksoai" ;;
    de) echo "Installiere...|Installiert! Tippe runkksoai zum Starten (API-Key beim ersten Start)|Befehl: runkksoai" ;;
    pt) echo "Instalando...|Instalado! Digite runkksoai para começar (chave API no primeiro uso)|Comando: runkksoai" ;;
    ru) echo "Установка...|Готово! Введите runkksoai, чтобы начать (API-ключ при первом запуске)|Команда: runkksoai" ;;
    id) echo "Menginstal...|Selesai! Ketik runkksoai untuk mulai (kunci API saat pertama)|Perintah: runkksoai" ;;
    ko) echo "설치 중...|설치 완료! runkksoai 를 입력하세요 (처음 실행 시 API 키 입력)|실행 명령: runkksoai" ;;
    vi) echo "Đang cài...|Xong! Gõ runkksoai để bắt đầu (từ khoá API lần đầu)|Lệnh chạy: runkksoai" ;;
    ar) echo "جارٍ التثبيت...|تم! اكتب runkksoai للبدء (مفتاح API عند أول تشغيل)|الأمر: runkksoai" ;;
    hi) echo "इंस्टॉल हो रहा है...|हो गया! शुरू करने के लिए runkksoai टाइप करें (पहली बार API Key)|कमांड: runkksoai" ;;
    *)  echo "Installing...|Installed! Type runkksoai to start (api key asked on first run)|Run command: runkksoai" ;;
  esac
}
IFS='|' read -r MSG_INSTALL MSG_DONE MSG_RUN <<< "$(localized "$LANG_CODE")"
echo "  ➜ $MSG_INSTALL"

# ---------- ติดตั้ง python/git (รองรับ Termux, apt, brew) ----------
ensure_pkg() {
  local cmd="$1" pkg="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "  ➜ installing $pkg ..."
    if [ "$IS_TERMUX" -eq 1 ]; then
      apt update -y && apt install -y "$pkg"
    elif command -v pkg >/dev/null 2>&1 && [ -n "$TERMUX_VERSION" ]; then
      pkg install -y "$pkg"
    elif command -v apt-get >/dev/null 2>&1; then
      (apt-get update && sudo apt-get install -y "$pkg") || apt-get install -y "$pkg"
    elif command -v dnf >/dev/null 2>&1; then
      sudo dnf install -y "$pkg"
    elif command -v pacman >/dev/null 2>&1; then
      sudo pacman -S --noconfirm "$pkg"
    elif command -v brew >/dev/null 2>&1; then
      brew install "$pkg"
    else
      echo "⚠️  please install '$pkg' manually"
      exit 1
    fi
  fi
}
ensure_pkg python3 python
ensure_pkg git git

# บันทึกภาษาที่เลือกไว้ใน config ของ CLI จริง (ไม่ถามซ้ำอีกตอนแชท)
SETLANG_OUT=$(python3 "$SCRIPT_DIR/runkksoai.py" --set-lang "$LANG_CODE" 2>&1) || true

# ---------- สร้างคำสั่ง runkksoai แบบเรียกได้จากทุกที่ ----------
install_launcher() {
  local dest="$1"
  cat > "$dest" <<EOF
#!/usr/bin/env bash
exec python3 "$SCRIPT_DIR/runkksoai.py" "\$@"
EOF
  chmod +x "$dest" 2>/dev/null || true
}

if [ "$IS_TERMUX" -eq 1 ]; then
  mkdir -p "$PREFIX/bin"
  install_launcher "$PREFIX/bin/runkksoai"
else
  if mkdir -p /usr/local/bin 2>/dev/null && [ -w /usr/local/bin ]; then
    install_launcher /usr/local/bin/runkksoai
  elif command -v sudo >/dev/null 2>&1 && command -v mktemp >/dev/null 2>&1; then
    # sudo เรียก bash function ตรงๆ ไม่ได้ — เขียนไฟล์ launcher ชั่วคราวแล้ว install ด้วยสิทธิ์ admin
    _tmp_launcher="$(mktemp)"
    printf '#!/usr/bin/env bash\nexec python3 "%s/runkksoai.py" "$@"\n' "$SCRIPT_DIR" > "$_tmp_launcher"
    chmod +x "$_tmp_launcher"
    if sudo install -m 755 "$_tmp_launcher" /usr/local/bin/runkksoai 2>/dev/null; then
      rm -f "$_tmp_launcher"
    else
      rm -f "$_tmp_launcher"
      mkdir -p "$HOME/.local/bin"
      install_launcher "$HOME/.local/bin/runkksoai"
    fi
  else
    mkdir -p "$HOME/.local/bin"
    install_launcher "$HOME/.local/bin/runkksoai"
    case ":$PATH:" in
      *":$HOME/.local/bin:"*) : ;;
      *)
        for RC in "$HOME/.bashrc" "$HOME/.profile"; do
          if [ -f "$RC" ] && ! grep -q '.local/bin' "$RC" 2>/dev/null; then
            printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$RC"
          fi
        done
        echo "  ℹ  launcher อยู่ที่ $HOME/.local/bin/runkksoai (เปิดเทอร์มินัลใหม่ หรือ export PATH ก่อนใช้)"
        ;;
    esac
  fi
fi

# ถ้าอยู่ในโฟลเดอร์โดยตรง ก็รัน ./runkksoai.py ได้เลย
chmod +x "$SCRIPT_DIR/runkksoai.py"

echo ""
echo "  ✔ $MSG_DONE"
echo "  ✔ $MSG_RUN"
echo ""
