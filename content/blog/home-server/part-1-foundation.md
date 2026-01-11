---
title: Part 1: The Foundation – Hardware & OS Setup
description: Setting up the hardware and foundation for your home media server
date: 2024-01-09
series: Home Server Setup
part: 1
total_parts: 5
slug: home-server-part-1-foundation
draft: true
---

This guide shows you how to turn a Raspberry Pi 5 into a powerful home media server. By the end, you will have:

1. **Runtipi** running easy-to-manage Docker containers.
2. **Plex** streaming locally and remotely (without VPN slowing it down).
3. **A "Magic" VPN Gateway** that lets your TV watch content from other countries (like the US) simply by changing a setting on your TV remote, while the Pi stays secure.

---

## Part 1: The Foundation (Storage & Runtipi)

Before installing apps, we need a stable base. This setup assumes you are using a **Raspberry Pi 5** with an **NVMe SSD** for speed and a large **USB HDD** for bulk storage.

### 1. Mount Your Drives Permanently

Linux drives need to be mounted to a specific folder to be visible to apps.

#### **Create mount points:**

```bash
sudo mkdir -p /mnt/nvme
sudo mkdir -p /mnt/hdd
```

#### **Find your Drive UUIDs:**

   Run `lsblk -f` and note the UUIDs for your NVMe and HDD partitions.

#### **Edit the Startup File:**

```bash
sudo nano /etc/fstab
```

Add these lines to the bottom (replace `UUID_HERE` with your actual IDs):

```ini
# NVMe Drive (Fast)
UUID=YOUR_NVME_UUID  /mnt/nvme  ext4  defaults,noatime  0  2

# USB HDD (Bulk Storage - NTFS)
UUID=YOUR_HDD_UUID   /mnt/hdd   ntfs-3g  defaults,nofail,uid=1000,gid=1000,umask=000  0  0
```

#### **Mount everything:**

```bash
sudo mount -a

```

### 2. Install Runtipi

Runtipi makes managing Docker containers incredibly easy.

```bash
curl -L https://runtipi.io/install | bash

```

Once installed, visit `http://YOUR_PI_IP` (e.g., `192.168.1.83`) in your browser to set up your dashboard.

---

## Part 2: Configuring Plex (The Right Way)

Many guides fail here by letting Docker hide your storage. We will map your drives explicitly so Plex can see everything.

### 1. Install Plex

In the Runtipi App Store, find **Plex** and click Install.

* **Open Port:** ON (Important for remote access)
* **Expose to Local Network:** ON

### 2. The "Trap Door" Fix

By default, Runtipi points Plex to the SD card. We need to point it to your NVMe/HDD.

#### **Stop Plex** via the Runtipi dashboard

#### **Edit the config via SSH:**

```bash
sudo nano ~/runtipi/app-data/plex/docker-compose.yml
```

#### **Update the `volumes` section:**

Remove the default `${ROOT_FOLDER_HOST}...` line and replace it with your real drives:

```yaml
volumes:
  - ${APP_DATA_DIR}/data/config:/config
  - ${APP_DATA_DIR}/data/transcode:/transcode
  # - ${ROOT_FOLDER_HOST}/media/data:/media  <-- DELETE THIS LINE
  - /mnt/nvme:/media/nvme
  - /mnt/hdd:/media/hdd
```

#### **Start Plex** again via the dashboard

Now, inside Plex, you can add libraries by browsing to `/media/nvme` or `/media/hdd`.

---

## Part 3: The "Hybrid" VPN Gateway

This is the killer feature. We will route the Raspberry Pi's traffic through a secure VPN (like ProtonVPN) **BUT** we will poke two specific holes in it:

1. **Hole 1:** Allow Plex to bypass the VPN so remote streaming is fast.
2. **Hole 2:** Create a bridge so your TV can use the VPN to watch foreign content.

### 1. Install WireGuard

```bash
sudo apt install wireguard openresolv
```

### 2. Configure the Interface

Create the config file:

```bash
sudo nano /etc/wireguard/wg0.conf
```

Paste this configuration (Use your own PrivateKey and Address from your VPN provider):

```ini
[Interface]
PrivateKey = YOUR_PRIVATE_KEY
Address = 10.2.0.2/32
DNS = 10.2.0.1
MTU = 1280  # Prevents "Connected but no internet" issues on TV

# --- THE HYBRID RULES ---

# 1. Split Tunnel (The Plex Bypass)
# Routes traffic from the Pi's own IP (e.g. .83) directly to the internet, skipping VPN.
PostUp = ip rule add from 192.168.1.83 table main priority 100
PostDown = ip rule del from 192.168.1.83 table main priority 100

# 2. Allow Forwarding (The "Docker Fix")
# Forces the firewall open so other devices (TV) can talk to the VPN.
PostUp = iptables -I FORWARD -j ACCEPT
PostDown = iptables -D FORWARD -j ACCEPT

# 3. NAT (Gateway Mode)
# Masquerades traffic so the TV looks like it's the Pi.
PostUp = iptables -t nat -A POSTROUTING -o %i -j MASQUERADE
PostDown = iptables -t nat -D POSTROUTING -o %i -j MASQUERADE

```

### 3. Start the VPN

```bash
sudo systemctl enable --now wg-quick@wg0
```

### 4. Enable Plex Remote Access

1. Go to your Router's Admin Page.
2. **Port Forward** TCP Port `32400` to your Pi's IP (`192.168.1.83`).
3. In Plex Settings > Remote Access:
   * Check **"Manually specify public port"** (32400).
   * Click Retry. It should turn Green!

---

## Part 4: How to Use It (The TV Trick)

Now you have a "Magic Switch" for your TV.

* **To Watch Local TV (No VPN):**
  Set your TV's Network Settings to **Automatic (DHCP)**.
* **To Watch US Content (VPN):**
  Set your TV's Network Settings to **Manual**:
  * **IP:** `192.168.1.150` (Unique IP)
  * **Gateway:** `192.168.1.83` (Your Pi's IP)
  * **DNS:** `1.1.1.1`

Enjoy your new Super-Server!
