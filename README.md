# BSI SQL Injection Lab

Laboratorium do zajęć z Bezpieczeństwa Systemów Informacyjnych:
- podatna aplikacja Flask,
- MariaDB,
- Adminer,
- attackbox,
- opcjonalnie Falco do obserwacji zdarzeń runtime.

## 1. Wymagania

Środowisko testowane pod Debianem 13.

Wymagane:
- Docker Engine
- Docker Compose plugin
- git
- przeglądarka WWW

Pakiety do zainstalowania:
```bash
#Instalacja dokera
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-doc podman-docker containerd runc | cut -f1) 2>/dev/null || true

sudo apt update
sudo apt install -y ca-certificates curl

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<'EOF'
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: trixie
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
#Instalacja przeglądarki Falkon
sudo apt install -y git falkon curl
