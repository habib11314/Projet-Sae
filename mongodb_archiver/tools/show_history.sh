#!/usr/bin/env bash
# show_history.sh - agrège et affiche l'historique de différents shells
# Usage:
#   show_history.sh [-n NUM] [-g PATTERN] [-r] [-s SHELL]
# Options:
#   -n NUM     : afficher les NUM dernières commandes (défaut 100)
#   -g PATTERN : filtrer par pattern (grep, takes regex)
#   -r         : afficher en ordre inverse (du plus ancien au plus récent)
#   -s SHELL   : forcer le shell source: bash|zsh|fish|pwsh
# Examples:
#   ./tools/show_history.sh -n 50
#   ./tools/show_history.sh -g "git" -n 200
#   ./tools/show_history.sh -s pwsh

set -euo pipefail
IFS=$'\n\t'

NUM=100
PATTERN=""
REVERSE=1
FORCE_SHELL=""

while getopts ":n:g:rs:" opt; do
  case ${opt} in
    n ) NUM=${OPTARG} ;;
    g ) PATTERN=${OPTARG} ;;
    r ) REVERSE=0 ;;
    s ) FORCE_SHELL=${OPTARG} ;;
    \? ) echo "Usage: $0 [-n NUM] [-g PATTERN] [-r] [-s SHELL]"; exit 1 ;;
  esac
done

# Collect candidate history files
declare -a files
# Bash
if [[ -n "${FORCE_SHELL}" && "${FORCE_SHELL}" != "bash" ]] || [[ -z "${FORCE_SHELL}" ]]; then
  if [[ -f "$HOME/.bash_history" ]]; then
    files+=("$HOME/.bash_history")
  fi
fi
# Zsh
if [[ -n "${FORCE_SHELL}" && "${FORCE_SHELL}" != "zsh" ]] || [[ -z "${FORCE_SHELL}" ]]; then
  if [[ -f "$HOME/.zsh_history" ]]; then
    files+=("$HOME/.zsh_history")
  fi
fi
# Fish
if [[ -n "${FORCE_SHELL}" && "${FORCE_SHELL}" != "fish" ]] || [[ -z "${FORCE_SHELL}" ]]; then
  if [[ -f "$HOME/.local/share/fish/fish_history" ]]; then
    files+=("$HOME/.local/share/fish/fish_history")
  fi
fi
# PowerShell (Windows) - transcription de l'history si présent
if [[ -n "${FORCE_SHELL}" && "${FORCE_SHELL}" != "pwsh" ]] || [[ -z "${FORCE_SHELL}" ]]; then
  # Common path for PowerShell Core on Linux; also try Windows-style (Git Bash / WSL mapping)
  if [[ -f "$HOME/.local/share/powershell/ConsoleHost_history.txt" ]]; then
    files+=("$HOME/.local/share/powershell/ConsoleHost_history.txt")
  fi
  if [[ -f "$HOME/.config/powershell/psh_history.txt" ]]; then
    files+=("$HOME/.config/powershell/psh_history.txt")
  fi
  # Also check Windows user profile path (when run under WSL/Git Bash, path may be accessible)
  if [[ -n "${WINDIR:-}" ]]; then
    winhist="$USERPROFILE\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
    if [[ -f "$winhist" ]]; then
      files+=("$winhist")
    fi
  fi
fi

# If FORCE_SHELL is set to specific shell, filter files accordingly
if [[ -n "$FORCE_SHELL" ]]; then
  case "$FORCE_SHELL" in
    bash) files=(); [[ -f "$HOME/.bash_history" ]] && files+=("$HOME/.bash_history") ;;
    zsh) files=(); [[ -f "$HOME/.zsh_history" ]] && files+=("$HOME/.zsh_history") ;;
    fish) files=(); [[ -f "$HOME/.local/share/fish/fish_history" ]] && files+=("$HOME/.local/share/fish/fish_history") ;;
    pwsh|powershell) files=(); [[ -f "$HOME/.local/share/powershell/ConsoleHost_history.txt" ]] && files+=("$HOME/.local/share/powershell/ConsoleHost_history.txt") ;;
    *) echo "Unknown shell: $FORCE_SHELL"; exit 2 ;;
  esac
fi

if [[ ${#files[@]} -eq 0 ]]; then
  echo "Aucun fichier d'historique trouvé dans les chemins connus." >&2
  exit 1
fi

# Function to normalize and stream commands from a history file
stream_history_file() {
  local f="$1"
  # Try to detect zsh extended history (starts with ': ' timestamps)
  if grep -q "^: [0-9]" "$f" 2>/dev/null; then
    # zsh extended history format: ": 1600000000:0;command"
    awk -F';' '{ sub(/^: [0-9]+:[0-9]+;/, ""); print }' "$f"
    return
  fi
  # Fish yaml-like history - lines starting with - cmd: |
  if grep -q "^- cmd:" "$f" 2>/dev/null; then
    awk '/^- cmd:/{getline; while($0 ~ /^\s/){sub(/^\s+/, "", $0); print; if(!getline) break}}' "$f"
    return
  fi
  # PowerShell ConsoleHost_history is plain lines, keep them
  # Bash history is plain lines too
  cat "$f"
}

# Aggregate histories (preserve order by file then line)
# Use a temporary file
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

for f in "${files[@]}"; do
  echo "# From: $f" >> "$tmpfile"
  stream_history_file "$f" >> "$tmpfile"
done

# Optionally filter by pattern
if [[ -n "$PATTERN" ]]; then
  # Use grep -i by default
  grep -i --color=always -E "$PATTERN" "$tmpfile" | tail -n "$NUM" | ( [[ $REVERSE -eq 1 ]] && tac || cat )
else
  tail -n "$NUM" "$tmpfile" | ( [[ $REVERSE -eq 1 ]] && tac || cat )
fi

exit 0
