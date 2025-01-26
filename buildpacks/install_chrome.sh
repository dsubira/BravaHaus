#!/bin/bash
set -e

echo "Configurant repositori de Google Chrome..."

# Afegir la clau GPG de Google Chrome
curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
