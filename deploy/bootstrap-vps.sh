#!/usr/bin/env bash
# One-time hardening + Docker install for a fresh Ubuntu 22.04/24.04 VPS.  Run as root:  bash bootstrap-vps.sh <deploy-user>
# It will NOT disable SSH password login unless <deploy-user> already has an authorized_keys file.
set -euo pipefail
USER_NAME="${1:?usage: bootstrap-vps.sh <deploy-user>}"
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get -y upgrade
apt-get -y install ca-certificates curl gnupg ufw fail2ban unattended-upgrades git rclone
# Docker (official repository)
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list
apt-get update && apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# deploy user
id "$USER_NAME" >/dev/null 2>&1 || adduser --disabled-password --gecos "" "$USER_NAME"
usermod -aG docker "$USER_NAME"
# firewall: only SSH, HTTP, HTTPS (database/redis are never published by the compose files)
ufw default deny incoming; ufw default allow outgoing
ufw allow 22/tcp; ufw allow 80/tcp; ufw allow 443/tcp
ufw --force enable
# automatic security updates + brute-force protection
dpkg-reconfigure -f noninteractive unattended-upgrades
systemctl enable --now fail2ban
# SSH hardening (only when key login is already set up)
if [ -s "/home/$USER_NAME/.ssh/authorized_keys" ]; then
  sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/; s/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
  systemctl reload ssh || systemctl reload sshd
  echo "SSH: password login and root login disabled."
else
  echo "NOTE: add your SSH public key to /home/$USER_NAME/.ssh/authorized_keys, then re-run this script to lock down SSH."
fi
mkdir -p /var/backups/garage && chown "$USER_NAME" /var/backups/garage
echo "Bootstrap complete. Log in as $USER_NAME and continue with docs/DEPLOYMENT.md"
