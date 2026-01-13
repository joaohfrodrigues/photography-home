---
title: Part 1: The Foundation – Hardware & OS Setup
description: Setting up the hardware and foundation for your home media server
date: 2026-01-13
series: Home Server Setup
part: 1
total_parts: 4
slug: home-server-part-1-foundation
---

Building a home server used to mean bulky towers and high electricity bills. Today, NAS Servers and mini PCs are very competitive, can be found for a couple hundred bucks and are easy to setup. Alongside them and as an possibly even cheaper alternative, there's the Raspberry Pi 5. It’s powerful enough to run a media center and stream at 4k, a VPN gateway, and home automation, all while sipping less power than a lightbulb.

In this series, we are going to build a **"Set and Forget"** home server. We will cover everything from handling high-speed storage to creating a "Teleportation Gateway" for your Smart TV.

**Part 1** focuses on the most critical (and often overlooked) step: **The Foundation.** Getting the storage and permissions right *now* will save you hours of "Permission Denied" errors later.

In the future I might do a similar setup on a proper NAS Server, but as I wanted to start small with the tools I had, saving costs and guaranteeing all my current needs are covered, a Raspberry Pi 5 proved to be enough.

## 🛠 The Hardware Stack

We aren't using SD cards for storage anymore. They are slow and prone to corruption.

* **Computation:** Raspberry Pi 5 (4GB or 8GB).
* **Storage:** NVMe SSD (M.2) connected via a USB 3.0 adapter or a dedicated hat. I used [this one (~15€)](https://shop.pimoroni.com/products/nvme-base?variant=41313839448147) from Pimoroni.
  > If you want to go a step further on storage configuration, check [these SATA hats](https://radxa.com/products/accessories/penta-sata-hat/) that support up to 5 SSDs.
* **OS Drive:** A small, high-quality SD card (just for booting the OS).

## Step 1: Headless OS Installation

We don't need a monitor or keyboard. We will set this up remotely.

1. Download the **Raspberry Pi Imager**.
2. Choose **Raspberry Pi OS Lite (64-bit)**. *We don't need a desktop interface slowing us down.*
3. **Advanced configuration:** Click the "Settings" (Gear icon) before writing.
    * **Hostname:** `homeserver` (or whatever you like).
    * **Enable SSH:** Use password authentication.
    * **Set Username/Password:** (e.g., `pi` / `yourpassword`).
    * **Configure Wireless LAN:** Enter your WiFi details (or just plug in Ethernet, which is better).
4. Write to the SD card, plug it into the Pi, and power it up.

## Step 2: Make sure storage is mounted

Unfortunately the storage drives we will use may not be automatically mounted. If you don't mount the drive permanently, your server will break the next time it reboots. To make sure the drive is mounted, we will use an ssh connection to the Raspberry Pi.

### Finding the drive and allocating the directory

``` bash
ssh pi@homeserver.local
# 1. Find the drive
# You are looking for your large SSD (usually named `sda` or `nvme0n1`).
lsblk
# 2. Format it (If new) *Warning: This wipes the drive.*
sudo mkfs.ext4 /dev/sda1
# 3. Create the Permanent Home
# We need a folder where this drive will live.
sudo mkdir -p /media/storage
```

### Mounting

We need to tell Linux to mount this drive automatically at boot.

``` bash
# First, get the drive's unique ID (UUID):
sudo blkid
# Copy the UUID string (e.g., `1234-5678-ABCD`), and edit the fstab file.
sudo nano /etc/fstab
# Add this line at the bottom
UUID=YOUR-UUID-HERE  /media/storage  ext4  defaults,noatime  0  2
```

  > **Why `noatime`?** It improves performance by telling the OS not to write a timestamp every time you read a file.

Test it immediately (do not reboot yet!):

``` bash
sudo mount -a
```

If you get no errors, you are safe. Below you find a screenshot of my mounted drives.

![Mounted drives](/content/blog/home-server/images/part-1-mounted-drives.png)

## Step 3: The Common Blindspot (Permissions)

This is where 90% of home server projects fail.
By default, the folder `/media/storage` is owned by `root`. But your apps (RunTipi, Plex, etc.) usually run as the user `pi` (UID 1000).

If you skip this, your apps will crash with "Permission Denied" when trying to save files.

**The Fix:**

``` bash
sudo chown -R 1000:1000 /media/storage
sudo chmod -R 775 /media/storage
```

* **`chown -R 1000:1000`**: This hands ownership of the drive (and everything inside it) to the standard user (UID 1000).
* **`chmod -R 775`**: This ensures the user and group have full Read/Write access.

## Step 4: Installing the Manager (RunTipi)

We could write `docker-compose` files manually, but **RunTipi** makes managing a home server incredibly easy. It handles updates, reverse proxies, and a beautiful dashboard for us.

Install it with one command:

``` bash
curl -L https://runtipi.io/install | bash
```

Once finished, open your browser and go to `http://homeserver.local`. You will be greeted by your new dashboard.

![Runtipi Dashboard](/content/blog/home-server/images/part-1-runtipi.png)

## Next Steps

Your foundation is rock solid. You have a high-speed NVMe drive that automatically mounts on boot, and—crucially—your applications actually have permission to write to it.

In **Part 2**, we will turn this quiet server into a media powerhouse by setting up **Plex**, handling hardware transcoding on the Pi 5, and automating your media library management.
