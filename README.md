# iPhone Backup Decryptor GUI

A clean, modern GUI for decrypting encrypted local iPhone backups on macOS and Windows — built on top of [jsharkey13/iphone_backup_decrypt](https://github.com/jsharkey13/iphone_backup_decrypt).

![Backup Decryptor Screenshot](screenshot.png)

---

## What it does

iTunes/Finder can create encrypted local backups of your iPhone. This app lets you unlock those backups and extract files from them — no command line needed.

You can extract:
- 📞 Call History
- 💬 SMS & iMessage
- 📷 Photos
- 💚 WhatsApp messages and attachments
- 🎙 Voicemail

---

## Requirements

- Python 3.8 or higher
- macOS or Windows

---

## Installation

**1. Clone the repo**
```bash
git clone https://github.com/yahyajavaid/iphone-backup-decrypt-gui.git
cd iphone-backup-decrypt-gui
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run**
```bash
python main.py
```

---

## How to use

1. **Select your backup folder** — on Mac it's usually:
   ```
   ~/Library/Application Support/MobileSync/Backup/<device-hash>
   ```
   On Windows:
   ```
   %AppData%\Apple Computer\MobileSync\Backup\<device-hash>
   ```
   Make sure you select the folder with the device hash, not its parent.

2. **Enter your backup password** — this is the password you set when enabling encrypted backups in iTunes or Finder.

3. **Click Unlock Backup** — the app will verify your password. This may take a few seconds due to the PBKDF2 key derivation.

4. **Select what to extract** — choose one or more categories, or click Select All.

5. **Choose an output folder** — where the decrypted files will be saved.

6. **Click Decrypt Backup** — files will be extracted to your output folder.

---

## Finding your backup folder

**Mac:**
1. Open Finder
2. Press `Cmd + Shift + G`
3. Paste: `~/Library/Application Support/MobileSync/Backup/`
4. Open the folder with the long hash name

**Windows:**
1. Press `Win + R`
2. Type: `%AppData%\Apple Computer\MobileSync\Backup\`
3. Open the folder with the long hash name

---

## Built on

This project is a GUI wrapper for [jsharkey13/iphone_backup_decrypt](https://github.com/jsharkey13/iphone_backup_decrypt). All decryption logic is handled by that library. Full credit to [@jsharkey13](https://github.com/jsharkey13) for the underlying implementation.

---

## License

MIT — see [LICENSE](LICENSE)
