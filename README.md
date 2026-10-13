# runkksoAi

AI Assistant CLI that can actually run bash commands — works on Termux, Linux, and macOS

## Features

- ✅ Installer has a menu — choose language 1, 2, 3, ... covering all languages (ไทย, English, 日本語, 中文, Español, Français, Deutsch, Português, Русский, Indonesia, 한국어, Tiếng Việt, العربية, हिन्दी)
- ✅ First launch shows a window to enter API Key and select provider: OpenAI, Groq, OpenRouter, Together AI, Google Gemini (OpenAI-compatible), Ollama (local), and other custom URLs
- ✅ AI can actually run bash commands on your machine (via function calling)
- ✅ **Every command the AI asks to run is confirmed first** (secure default) — file-deleting commands (rm, rmdir, unlink, shred, find -delete, truncate, etc.) get an extra "delete mode" warning and always ask again, no exceptions
- ✅ Machine-destroying commands (rm -rf /, mkfs, dd of=/dev/...) are rejected immediately — not even asked
- ✅ Unknown custom Base URL → you must confirm before the API key is sent there (trusted hosts are remembered in config)
- ✅ Risk-based options: `--auto` (skip confirmation for normal commands — deletion still always asks) and `"work_dir": "/path"` in config to limit the working directory for commands
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
pkg update && pkg install git python -y && git clone https://github.com/kkso882/runkksoAi runkksoAi && cd runkksoAi && bash install.sh
```
Chat commands: `/exit` quit • `/new` new chat • `/setup` configure API • `/lang` change language • `/help`

Options: `--setup` (open setup window again), `--lang th` (set language), `--auto` (**accepted risk** — skip confirmation for normal commands), `echo "hi" | runkksoai` (pipe mode: AI-requested commands are auto-**denied** when no one can confirm — use `--auto` if you intend that)

## File Structure

```
runkksoAi/
├── install.sh     # Installer with language menu 1,2,3,... (Termux/Linux/macOS)
├── runkksoai.py   # Main AI CLI (Python stdlib only — no pip required)
└── README.md
```

*Still a demo — there may be bugs*

## Developer

- https://github.com/kkso882
