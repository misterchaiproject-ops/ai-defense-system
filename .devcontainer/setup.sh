#!/bin/bash
set -euo pipefail

# Git: no pager, no CRLF, no rebase surprises
git config --global core.pager cat
git config --global core.autocrlf false
git config --global pull.rebase false
git config --global init.defaultBranch main

# Bash: disable bracketed paste auto-indent (Tab S9 fix)
if [ -f "$HOME/.inputrc" ]; then
    cp "$HOME/.inputrc" "$HOME/.inputrc.bak"
fi
printf "set enable-bracketed-paste off\nset bell-style none\n" > "$HOME/.inputrc"

# uv: prefer hardlink (Codespaces fix)
export UV_LINK_MODE=copy

printf "=== DEVCONTAINER SETUP COMPLETE ===\n"
git config --global --list | grep -E "pager|autocrlf|rebase|defaultBranch"
