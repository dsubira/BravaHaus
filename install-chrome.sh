#!/bin/bash
set -e

# Afegir la font de Google Chrome
echo "deb [signed-by=/usr/share/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# Importar la clau GPG per al repositori
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /usr/share/keyrings/google-chrome.gpg

# Actualitzar l'índex de paquets
apt-get update

# Instal·lar Google Chrome
apt-get install -y google-chrome-stable
