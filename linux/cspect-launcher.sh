#!/bin/sh
# CSpect Launcher for Linux - start script
# (c) 2026 Giuseppe Papa - GPL-3.0 - https://github.com/Saxabar/CSpectLauncher
cd "$(dirname "$0")" || exit 1
exec python3 launcher.py "$@"
