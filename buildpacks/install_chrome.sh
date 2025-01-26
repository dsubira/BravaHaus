#!/bin/bash
set -e

echo "Afegint repositori oficial de Google Chrome..."

# Afegir repositori de Google Chrome
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    | tee /etc/apt/sources.list.d/google-chrome.list

# Importar la clau GPG de Google Chrome
curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg

echo "Actualitzant i instal·lant Google Chrome..."

# Actualitzar paquets i instal·lar Chrome
apt-get update && apt-get install -y google-chrome-stable

echo "Google Chrome instal·lat correctament!"
