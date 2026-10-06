#!/bin/bash
git config --global core.pager cat git config --global core.autocrlf false git config
--global pull.rebase false echo "set enable-bracketed-paste off" > ~/.inputrc echo
"=== SETUP COMPLETE ==="
git config --global --list | grep pager
