# AES-256 Ransomware PoC

**Educational Proof of Concept** – a simple ransomware demonstration written in Python.

> ⚠️ **IMPORTANT WARNING**
> This project is intended **for educational and research purposes only**.
> **Do not run** these scripts on a computer containing important data. Permanent data loss may occur.

---

## 📋 Project Description

This repository contains two versions of a simple ransomware implementation:

* **`encryptor.py`** – manual version (the user selects files)
* **`encryptor_auto.py`** – automatic version (encrypts almost all files in the user's directory)

Both versions use **strong AES-256-GCM encryption**.

---

## ✨ Features

### Shared Features

* AES-256-GCM encryption (authenticated encryption)
* PBKDF2-HMAC-SHA256 key derivation (200,000 iterations)
* In-place file encryption
* Lock screen (LockScreen)
* Desktop wallpaper replacement with a ransom notice
* Termination of common applications
* Audio notification playback (`sound.mp3`)
* Automatic decryption after entering the correct password

### encryptor.py

* Manual file selection through a GUI
* User-defined password

### encryptor_auto.py

* Automatically scans the user's directory (`C:\Users\Username`)
* Skips system folders
* Fixed password: `123456`

---

## 🛠️ Technical Information

* **Language**: Python 3
* **Libraries**: `cryptography`, `Pillow`, `tkinter`, `pygame` (installed automatically)
* **Platform**: Primarily Windows
* **Encryption**: AES-256-GCM + PBKDF2

---

## ⚠️ Warning

* Without the correct password, files are **unrecoverable**.
* Large files may cause the program to crash (the entire file is loaded into RAM).
* Antivirus software (especially Windows Defender) will usually detect and block the scripts.
* The lock screen can be bypassed by restarting the computer or terminating the Python process.
* **Test exclusively inside a virtual machine!**

---

## 🚀 How to Run

1. Download the repository
2. Run `encryptor.py` or `encryptor_auto.py`
3. Accept the disclaimer
4. Manual version: select files and enter a password
5. Automatic version: encryption starts immediately

Decryption is performed automatically after entering the correct password on the lock screen.

---

## 🎯 Project Goal

This repository is intended to demonstrate:

* How ransomware works on a technical level
* Implementation of modern cryptography in Python
* Social engineering GUI concepts
* System manipulation (wallpaper, processes)

**Designed for students, security researchers, and malware analysts.**

---

## ⚖️ Disclaimer

This project is provided "as is." The author assumes no responsibility for any damage resulting from misuse.

---

**Status:** Educational Proof of Concept
