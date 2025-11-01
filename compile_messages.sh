#!/bin/bash
# Script to compile translation messages
# Requires gettext to be installed

cd "$(dirname "$0")"

if command -v msgfmt &> /dev/null; then
    echo "Compiling Russian translation messages..."
    msgfmt -o locale/ru/LC_MESSAGES/django.mo locale/ru/LC_MESSAGES/django.po
    echo "Translation messages compiled successfully!"
else
    echo "Error: msgfmt not found. Please install gettext."
    echo "On macOS: brew install gettext"
    echo "On Ubuntu/Debian: sudo apt-get install gettext"
    echo "On Docker: apt-get update && apt-get install -y gettext"
fi
