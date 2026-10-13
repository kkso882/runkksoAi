# runkksoAi

AI Assistant CLI that can actually run bash commands — works on Termux, Linux, and macOS

## Features

- ✅ Installer has a menu — choose language 1, 2, 3, ... covering all languages (Thai, English, 日本語, 中文, Español, Français, Deutsch, Português, Русский, Indonesia, 한국어, Tiếng Việt, العربية, हिन्दी)
- ✅ First launch shows a window to enter API Key and select provider: OpenAI, Groq, OpenRouter, Together AI, Google Gemini (OpenAI-compatible), Ollama (local), and other custom URLs
- ✅ AI can actually run bash commands on your machine (via function calling)
- ✅ Any file-deleting command (rm, rmdir, unlink, shred, find -delete, truncate, etc.) will always ask for confirmation — no exceptions
- ✅ Machine-destroying commands (rm -rf /, mkfs, dd of=/dev/...) are rejected immediately
- ✅ API Key is stored in `~/.runkksoai/config.json` with 0600 permissions and is never sent anywhere else

## Install on Termux

```bash
pkg update && pkg install git python -y
git clone <repo-url> runkksoAi
cd runkksoAi
bash install.sh      # choose language 1,2,3,... then it installs automatically
```


When finished, type:

```bash
runkksoai            # first time it will open the API Key setup window
```

## Chat Usage

```
[You] > What’s in this folder?
  ⚡ $ ls -la
[AI] There are files ...

[You] > Delete old.log
  🗑  mode: delete — rm old.log
⚠️  This command will **delete a file** — confirm? (y/n): y
  ⚡ $ rm old.log
```
## All in 1 
```bash
pkg update && pkg install git python -y && git clone https://github.com/kkso8882kkkso9882-prog/runkksoAi runkksoAi && cd runkksoAi && bash install.sh
```
Chat commands: `/exit` quit • `/new` new chat • `/setup` configure API • `/lang` change language • `/help`

Options: `--setup` (open setup window again), `--lang th` (set language), `echo "hi" | runkksoai` (pipe mode)

## File Structure

```
runkksoAi/
├── install.sh     # Installer with language menu 1,2,3,... (Termux/Linux/macOS)
├── runkksoai.py   # Main AI CLI (Python stdlib only — no pip required)
└── README.md
```

## Developer

- Roblox: https://www.roblox.com/en/users/5509501038/profile
- YouTube: https://youtube.com/@kkso882?si=4AfUoiWQ4fUVXcUU
- Still a demo — there may be bugs
