import tkinter as tk
from tkinter import ttk, filedialog
import threading
import os

# ── Palette ───────────────────────────────────────────────────────────────────
BG         = "#0a0a0f"
GLASS      = "#ffffff0d"   # not real alpha — we simulate with close color
GLASS_STR  = "#18181f"
GLASS_HOV  = "#22222c"
BORDER     = "#2a2a38"
BORDER_LT  = "#3a3a50"
ACCENT     = "#6c63ff"
ACCENT2    = "#a78bfa"
TEXT       = "#f0f0ff"
TEXT_SEC   = "#8888aa"
TEXT_DIM   = "#44445a"
SUCCESS    = "#34d399"
ERROR      = "#f87171"
WARN       = "#fbbf24"

# Fonts
try:
    import tkinter.font as tkfont
    _f = tkfont.Font(family="SF Pro Display")
    IS_MAC = _f.actual("family") == "SF Pro Display"
except Exception:
    IS_MAC = False

FH  = ("SF Pro Display", 22, "bold")  if IS_MAC else ("Helvetica Neue", 22, "bold")
FT  = ("SF Pro Display", 13, "bold")  if IS_MAC else ("Helvetica Neue", 13, "bold")
FB  = ("SF Pro Text",    12)          if IS_MAC else ("Helvetica Neue", 12)
FS  = ("SF Pro Text",    10)          if IS_MAC else ("Helvetica Neue", 10)
FM  = ("SF Mono",        10)          if IS_MAC else ("Courier New",    10)


# ── Helpers ───────────────────────────────────────────────────────────────────

def pill_button(parent, text, cmd, accent=True, small=False, **kw):
    bg  = ACCENT      if accent else GLASS_STR
    fg  = "#ffffff"   if accent else TEXT_SEC
    hbg = "#5a52e0"   if accent else GLASS_HOV
    pad = (14, 6) if small else (22, 10)
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=fg,
                  activebackground=hbg, activeforeground="#fff",
                  relief="flat", bd=0, cursor="hand2",
                  font=(FT[0], 11, "bold") if not small else (FB[0], 10),
                  padx=pad[0], pady=pad[1], **kw)
    b.bind("<Enter>", lambda _: b.config(bg=hbg))
    b.bind("<Leave>", lambda _: b.config(bg=bg))
    return b

def glass_frame(parent, **kw):
    return tk.Frame(parent, bg=GLASS_STR,
                    highlightthickness=1,
                    highlightbackground=BORDER, **kw)

def field(parent, show=None, **kw):
    e = tk.Entry(parent, bg="#111120", fg=TEXT,
                 insertbackground=ACCENT2,
                 relief="flat",
                 highlightthickness=1,
                 highlightbackground=BORDER,
                 highlightcolor=ACCENT,
                 font=FB, show=show,
                 **kw)
    return e

def row_label(parent, text, **kw):
    return tk.Label(parent, text=text, bg=GLASS_STR,
                    fg=TEXT, font=FB, **kw)

def section_label(parent, text):
    f = tk.Frame(parent, bg=BG)
    f.pack(fill="x", padx=28, pady=(20, 6))
    tk.Label(f, text=text, bg=BG, fg=ACCENT2,
             font=(FS[0], 9, "bold")).pack(side="left")

def hairline(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=0)

def section_lbl(parent, text):
    f = tk.Frame(parent, bg=BG)
    f.pack(fill="x", padx=4, pady=(16, 4))
    tk.Label(f, text=text, bg=BG, fg=ACCENT2, font=(FS[0], 9, "bold")).pack(side="left")


# ══════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):

    CATEGORIES = [
        ("call",      "Call History",   "📞"),
        ("sms",       "SMS & iMessage", "💬"),
        ("photos",    "Photos",         "🖼"),
        ("whatsapp",  "WhatsApp",       "💚"),
        ("voicemail", "Voicemail",      "🎙"),
    ]

    def __init__(self):
        super().__init__()
        self.title("Backup Decryptor")
        self.configure(bg=BG)
        self.resizable(False, True)
        self.backup       = None
        self._done_files  = 0
        self._real_folder = ""
        self._real_output = ""

        # scrollable canvas, no visible scrollbar
        self._canvas = tk.Canvas(self, bg=BG, highlightthickness=0, width=880)
        self._canvas.pack(fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=BG)
        self._wid   = self._canvas.create_window((0,0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._wid, width=e.width))
        def _scroll(e):
            # macOS trackpad sends large deltas, normalize them
            delta = e.delta
            if abs(delta) > 10:
                delta = delta // 120
            self._canvas.yview_scroll(-delta, "units")

        self._canvas.bind_all("<MouseWheel>", _scroll)
        # macOS two-finger trackpad scroll
        self._canvas.bind_all("<Button-4>",
            lambda e: self._canvas.yview_scroll(-1, "units"))
        self._canvas.bind_all("<Button-5>",
            lambda e: self._canvas.yview_scroll(1, "units"))

        self._build()

        self.update_idletasks()
        content_h = self._inner.winfo_reqheight()
        screen_h  = self.winfo_screenheight() - 100
        win_h     = min(content_h, screen_h)
        self.geometry("880x660")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-880)//2}+{(sh-660)//2}")

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        p = self._inner

        # Header
        hdr = tk.Frame(p, bg=BG)
        hdr.pack(fill="x", padx=32, pady=(28,16))
        dot = tk.Frame(hdr, bg=ACCENT, width=6, height=6)
        dot.pack(side="left", padx=(0,12), pady=8)
        col = tk.Frame(hdr, bg=BG)
        col.pack(side="left")
        tk.Label(col, text="Backup Decryptor", bg=BG, fg=TEXT, font=FH).pack(anchor="w")
        tk.Label(col, text="Decrypt encrypted iPhone backups", bg=BG, fg=TEXT_SEC, font=FS).pack(anchor="w", pady=(2,0))

        # Two column body
        body = tk.Frame(p, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0,28))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        # LEFT
        left = tk.Frame(body, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))

        section_lbl(left, "BACKUP LOCATION")
        loc = glass_frame(left)
        loc.pack(fill="x", pady=(4,0))

        fr = tk.Frame(loc, bg=GLASS_STR)
        fr.pack(fill="x", padx=18, pady=(16,0))
        row_label(fr, "Folder").pack(side="left")
        pill_button(fr, "Browse", self._pick_folder, accent=False, small=True).pack(side="right")
        self._folder_disp = tk.Label(loc, text="No folder selected",
                                      bg=GLASS_STR, fg=TEXT_DIM, font=FS, anchor="w", wraplength=320, justify="left")
        self._folder_disp.pack(fill="x", padx=18, pady=(4,14))

        tk.Frame(loc, bg=BORDER, height=1).pack(fill="x")
        pr = tk.Frame(loc, bg=GLASS_STR)
        pr.pack(fill="x", padx=18, pady=(14,0))
        row_label(pr, "Password").pack(side="left")
        self._show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(pr, text="Show", variable=self._show_var,
                       command=lambda: self._pass_e.config(show="" if self._show_var.get() else "•"),
                       bg=GLASS_STR, fg=TEXT_DIM, activebackground=GLASS_STR,
                       selectcolor=GLASS_STR, font=FS, cursor="hand2", relief="flat", bd=0).pack(side="right")
        self.pass_var = tk.StringVar()
        self._pass_e = field(pr, show="•", textvariable=self.pass_var)
        self._pass_e.pack(side="right", padx=(0,8), fill="x", expand=True)
        self._pass_e.bind("<Return>", lambda _: self._do_validate())

        tk.Frame(loc, bg=BORDER, height=1).pack(fill="x", pady=(14,0))
        unlock_row = tk.Frame(loc, bg=GLASS_STR)
        unlock_row.pack(fill="x", padx=18, pady=14)
        self._val_btn = pill_button(unlock_row, "Unlock Backup", self._do_validate)
        self._val_btn.pack(side="left")
        self._val_lbl = tk.Label(unlock_row, text="", bg=GLASS_STR, fg=TEXT_SEC, font=FS)
        self._val_lbl.pack(side="left", padx=(12,0))

        section_lbl(left, "OUTPUT FOLDER")
        out_card = glass_frame(left)
        out_card.pack(fill="x", pady=(4,0))
        out_row = tk.Frame(out_card, bg=GLASS_STR)
        out_row.pack(fill="x", padx=18, pady=(16,0))
        row_label(out_row, "Save to").pack(side="left")
        self._out_btn = pill_button(out_row, "Browse", self._pick_output, accent=False, small=True, state="disabled")
        self._out_btn.pack(side="right")
        self._out_disp = tk.Label(out_card, text="No folder selected",
                                   bg=GLASS_STR, fg=TEXT_DIM, font=FS, anchor="w", wraplength=320, justify="left")
        self._out_disp.pack(fill="x", padx=18, pady=(4,16))

        section_lbl(left, "PROGRESS")
        prog_card = glass_frame(left)
        prog_card.pack(fill="x", pady=(4,0))
        pi = tk.Frame(prog_card, bg=GLASS_STR)
        pi.pack(fill="x", padx=18, pady=16)
        top_row = tk.Frame(pi, bg=GLASS_STR)
        top_row.pack(fill="x", pady=(0,8))
        self._prog_status = tk.Label(top_row, text="Waiting for backup…",
                                      bg=GLASS_STR, fg=TEXT_SEC, font=FS, anchor="w")
        self._prog_status.pack(side="left")
        self._prog_count = tk.Label(top_row, text="", bg=GLASS_STR, fg=ACCENT2, font=(FS[0],FS[1],"bold"))
        self._prog_count.pack(side="right")
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("gls.Horizontal.TProgressbar",
                        troughcolor=BORDER, background=TEXT_DIM,
                        bordercolor=GLASS_STR, lightcolor=TEXT_DIM, darkcolor=TEXT_DIM, thickness=3)
        self._prog_bar = ttk.Progressbar(pi, style="gls.Horizontal.TProgressbar",
                                          orient="horizontal", mode="determinate", maximum=100)
        self._prog_bar.pack(fill="x")

        tk.Frame(left, bg=BG, height=14).pack()
        self._decrypt_btn = pill_button(left, "Decrypt Backup", self._do_decrypt, state="disabled")
        self._decrypt_btn.config(pady=12, font=(FT[0], 13, "bold"))
        self._decrypt_btn.pack(fill="x")

        # RIGHT
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(10,0))

        section_lbl(right, "WHAT TO EXTRACT")
        self._ext_card = glass_frame(right)
        self._ext_card.pack(fill="x", pady=(4,0))

        self._cat_vars = {}
        self._cat_rows_ui = {}

        for i, (key, lbl, icon) in enumerate(self.CATEGORIES):
            if i > 0:
                tk.Frame(self._ext_card, bg=BORDER, height=1).pack(fill="x")
            var = tk.BooleanVar(value=False)
            self._cat_vars[key] = var
            row = tk.Frame(self._ext_card, bg=GLASS_STR, cursor="hand2")
            row.pack(fill="x")
            self._cat_rows_ui[key] = row
            inner = tk.Frame(row, bg=GLASS_STR)
            inner.pack(fill="x", padx=18, pady=13)
            icon_lbl = tk.Label(inner, text=icon, bg=GLASS_STR, font=("",14))
            icon_lbl.pack(side="left", padx=(0,10))
            name_lbl = tk.Label(inner, text=lbl, bg=GLASS_STR, fg=TEXT_DIM, font=FB)
            name_lbl.pack(side="left")
            tog = tk.Label(inner, text="  ○  ", bg=GLASS_STR, fg=TEXT_DIM, font=(FS[0],11))
            tog.pack(side="right")
            var._name_lbl = name_lbl
            var._tog      = tog
            var._row      = row
            var._enabled  = False

            def make_toggle(v, nm, tg, rw):
                def on_click(e=None):
                    if not v._enabled: return
                    v.set(not v.get())
                    self._refresh_toggle(v, nm, tg, rw)
                    self._on_cat_change()
                return on_click

            fn = make_toggle(var, name_lbl, tog, row)
            for w in (row, inner, icon_lbl, name_lbl, tog):
                w.bind("<Button-1>", fn)

        tk.Frame(self._ext_card, bg=BORDER, height=1).pack(fill="x")
        sa_row = tk.Frame(self._ext_card, bg=GLASS_STR, cursor="hand2")
        sa_row.pack(fill="x")
        sa_inner = tk.Frame(sa_row, bg=GLASS_STR)
        sa_inner.pack(fill="x", padx=18, pady=13)
        self._sa_lbl = tk.Label(sa_inner, text="Select All", bg=GLASS_STR, fg=TEXT_DIM, font=(FB[0],FB[1],"bold"))
        self._sa_lbl.pack(side="left")
        self._sa_tog = tk.Label(sa_inner, text="  ○  ", bg=GLASS_STR, fg=TEXT_DIM, font=(FS[0],11))
        self._sa_tog.pack(side="right")
        self._sa_all = tk.BooleanVar(value=False)
        self._sa_all._enabled = False

        def toggle_all(e=None):
            if not self._sa_all._enabled: return
            self._sa_all.set(not self._sa_all.get())
            for k, v in self._cat_vars.items():
                v.set(self._sa_all.get())
                self._refresh_toggle(v, v._name_lbl, v._tog, v._row)
            self._refresh_sa()
            self._on_cat_change()

        for w in (sa_row, sa_inner, self._sa_lbl, self._sa_tog):
            w.bind("<Button-1>", toggle_all)

        self._cat_hint = tk.Label(right, text="Unlock your backup first to enable.",
                                   bg=BG, fg=TEXT_DIM, font=FS)
        self._cat_hint.pack(anchor="w", padx=4, pady=(6,0))

        section_lbl(right, "LOG")
        log_card = glass_frame(right)
        log_card.pack(fill="both", expand=True, pady=(4,0))
        self._log = tk.Text(log_card, bg=GLASS_STR, fg=TEXT_SEC, font=FM,
                             relief="flat", bd=0, height=12,
                             state="disabled", wrap="word",
                             insertbackground=ACCENT, selectbackground=BORDER,
                             padx=16, pady=12)
        self._log.pack(fill="both", expand=True)
        self._log.tag_config("ok",   foreground=SUCCESS)
        self._log.tag_config("err",  foreground=ERROR)
        self._log.tag_config("warn", foreground=WARN)
        self._log.tag_config("dim",  foreground=TEXT_DIM)

    def _refresh_toggle(self, var, name_lbl, tog, row):
        if var.get():
            name_lbl.config(fg=TEXT)
            tog.config(text="  ●  ", fg=ACCENT2)
            row.config(bg=GLASS_HOV)
            for w in row.winfo_children():
                w.config(bg=GLASS_HOV)
                for ww in w.winfo_children():
                    try: ww.config(bg=GLASS_HOV)
                    except: pass
        else:
            name_lbl.config(fg=TEXT_DIM)
            tog.config(text="  ○  ", fg=TEXT_DIM)
            row.config(bg=GLASS_STR)
            for w in row.winfo_children():
                w.config(bg=GLASS_STR)
                for ww in w.winfo_children():
                    try: ww.config(bg=GLASS_STR)
                    except: pass

    def _refresh_sa(self):
        all_on = all(v.get() for v in self._cat_vars.values())
        self._sa_all.set(all_on)
        if all_on:
            self._sa_lbl.config(fg=TEXT)
            self._sa_tog.config(text="  ●  ", fg=ACCENT2)
        else:
            self._sa_lbl.config(fg=TEXT_DIM)
            self._sa_tog.config(text="  ○  ", fg=TEXT_DIM)

    # ── Pickers ───────────────────────────────────────────────────────────────

    def _pick_folder(self):
        p = filedialog.askdirectory(title="Select iPhone Backup Folder")
        if not p:
            return
        self._real_folder = p
        parts = p.split("/")
        display = "…/" + parts[-1] if len(parts) > 1 else p
        self._folder_disp.config(text=display, fg=TEXT_SEC)
        if not os.path.exists(os.path.join(p, "Manifest.db")):
            self._val_lbl.config(
                text="⚠  Select the hash folder, not its parent", fg=WARN)
        else:
            self._val_lbl.config(text="", fg=TEXT_SEC)
        if self.backup:
            self.backup = None
            self._lock_categories()

    def _pick_output(self):
        p = filedialog.askdirectory(title="Select Output Folder")
        if not p:
            return
        self._real_output = p
        parts = p.split("/")
        display = "…/" + parts[-1] if len(parts) > 1 else p
        self._out_disp.config(text=display, fg=TEXT_SEC)

    # ── Category lock / unlock ────────────────────────────────────────────────

    def _lock_categories(self):
        for var in self._cat_vars.values():
            var._enabled = False
            var.set(False)
            self._refresh_toggle(var, var._name_lbl, var._tog, var._row)
        self._sa_all._enabled = False
        self._sa_lbl.config(fg=TEXT_DIM)
        self._sa_tog.config(text="  ○  ", fg=TEXT_DIM)
        self._out_btn.config(state="disabled")
        self._decrypt_btn.config(state="disabled")
        self._cat_hint.config(text="Unlock your backup first to select files.")

    def _unlock_categories(self):
        for var in self._cat_vars.values():
            var._enabled = True
            var._name_lbl.config(fg=TEXT_SEC)
        self._sa_all._enabled = True
        self._sa_lbl.config(fg=TEXT_SEC)
        self._out_btn.config(state="normal")
        self._cat_hint.config(text="")
        style = ttk.Style(self)
        style.configure("gls.Horizontal.TProgressbar",
                        background=ACCENT, lightcolor=ACCENT, darkcolor=ACCENT)
        self._prog_status.config(text="Select files and press Decrypt.")

    def _on_cat_change(self):
        any_on = any(v.get() for v in self._cat_vars.values())
        self._decrypt_btn.config(
            state="normal" if (any_on and self.backup) else "disabled")
        self._refresh_sa()

    # ── Validation ────────────────────────────────────────────────────────────

    def _do_validate(self):
        folder = self._real_folder
        pw     = self.pass_var.get()
        if not folder:
            self._val_lbl.config(text="Choose a folder first.", fg=WARN)
            return
        if not os.path.exists(os.path.join(folder, "Manifest.db")):
            self._val_lbl.config(
                text="⚠  No Manifest.db — select the hash folder", fg=WARN)
            return
        if not pw:
            self._val_lbl.config(text="Enter your password.", fg=WARN)
            return
        self._val_btn.config(state="disabled")
        self._val_lbl.config(text="Verifying…", fg=TEXT_SEC)
        threading.Thread(target=self._validate_worker,
                         args=(folder, pw), daemon=True).start()

    def _validate_worker(self, folder, pw):
        try:
            from iphone_backup_decrypt import EncryptedBackup
        except ImportError:
            self.after(0, self._val_done, None,
                       "Run: pip install iphone_backup_decrypt")
            return
        try:
            bk = EncryptedBackup(backup_directory=folder, passphrase=pw)
            ok = bk.test_decryption()
            self.after(0, self._val_done, bk if ok else None,
                       None if ok else "wrong_password")
        except Exception as exc:
            self.after(0, self._val_done, None, str(exc))

    def _val_done(self, backup_obj, err):
        self._val_btn.config(state="normal")
        if backup_obj:
            self.backup = backup_obj
            self._val_lbl.config(text="✓  Unlocked", fg=SUCCESS)
            if not self._real_output:
                self._real_output = os.path.join(self._real_folder, "decrypted")
                self._out_disp.config(text="…/decrypted", fg=TEXT_SEC)
            self._unlock_categories()
            self._log_write("Backup unlocked. Select files to extract.", "ok")
        elif err == "wrong_password":
            self._val_lbl.config(text="✗  Incorrect password", fg=ERROR)
        else:
            self._val_lbl.config(text=f"✗  {err}", fg=ERROR)

    # ── Decryption ────────────────────────────────────────────────────────────

    def _do_decrypt(self):
        out = self._real_output
        if not out:
            self._prog_status.config(text="Choose an output folder.", fg=WARN)
            return
        os.makedirs(out, exist_ok=True)
        opts = {k: v.get() for k, v in self._cat_vars.items()}
        self._decrypt_btn.config(state="disabled")
        self._val_btn.config(state="disabled")
        self._done_files  = 0
        self._total_tasks = max(sum(1 for v in opts.values() if v), 1)
        self._done_tasks  = 0
        self._prog_bar.config(value=0)
        self._prog_status.config(text="Starting…", fg=TEXT_SEC)
        self._log_write(f"Output → {out}", "dim")
        threading.Thread(target=self._decrypt_worker,
                         args=(out, opts), daemon=True).start()

    def _decrypt_worker(self, out, opts):
        try:
            from iphone_backup_decrypt import RelativePath, MatchFiles
        except ImportError:
            self.after(0, self._log_write, "iphone_backup_decrypt not installed", "err")
            self.after(0, self._finish, False)
            return

        # Recreate EncryptedBackup in this thread — SQLite objects can't be
        # shared across threads (created during validation in a different thread)
        try:
            from iphone_backup_decrypt import EncryptedBackup
            backup = EncryptedBackup(
                backup_directory=self._real_folder,
                passphrase=self.pass_var.get()
            )
        except Exception as exc:
            self.after(0, self._log_write, f"Failed to open backup: {exc}", "err")
            self.after(0, self._finish, False)
            return
        all_ok = True

        def tick():
            self._done_tasks += 1
            pct = int(self._done_tasks / self._total_tasks * 100)
            self.after(0, self._prog_bar.config, {"value": pct})

        def single(label, rel_path, outfile):
            nonlocal all_ok
            self.after(0, self._prog_status.config,
                       {"text": f"Extracting {label}…", "fg": TEXT_SEC})
            self.after(0, self._log_write, f"Extracting {label}…", "dim")
            try:
                backup.extract_file(relative_path=rel_path, output_filename=outfile)
                self._done_files += 1
                self.after(0, self._prog_count.config,
                           {"text": f"{self._done_files} files"})
                self.after(0, self._log_write, f"{label} — done", "ok")
            except Exception as exc:
                self.after(0, self._log_write, f"{label} — {exc}", "err")
                all_ok = False
            tick()

        def bulk(label, match_kw, out_folder, **kw):
            nonlocal all_ok
            self.after(0, self._prog_status.config,
                       {"text": f"Extracting {label}…", "fg": TEXT_SEC})
            self.after(0, self._prog_bar.config, {"mode": "indeterminate"})
            self.after(0, self._prog_bar.start, 10)
            self.after(0, self._log_write, f"Extracting {label}…", "dim")
            try:
                count = backup.extract_files(**match_kw, output_folder=out_folder, **kw)
                self._done_files += (count or 0)
                self.after(0, self._prog_bar.stop)
                self.after(0, self._prog_bar.config, {"mode": "determinate"})
                self.after(0, self._prog_count.config,
                           {"text": f"{self._done_files} files"})
                self.after(0, self._log_write,
                           f"{label} — {count or 0} files", "ok")
            except Exception as exc:
                self.after(0, self._prog_bar.stop)
                self.after(0, self._prog_bar.config, {"mode": "determinate"})
                self.after(0, self._log_write, f"{label} — {exc}", "err")
                all_ok = False
            tick()

        if opts.get("call"):
            single("Call History", RelativePath.CALL_HISTORY,
                   os.path.join(out, "call_history.sqlite"))
        if opts.get("sms"):
            single("SMS & iMessage", RelativePath.TEXT_MESSAGES,
                   os.path.join(out, "sms.sqlite"))
        if opts.get("photos"):
            bulk("Photos", MatchFiles.CAMERA_ROLL, os.path.join(out, "photos"))
        if opts.get("whatsapp"):
            single("WhatsApp DB", RelativePath.WHATSAPP_MESSAGES,
                   os.path.join(out, "whatsapp.sqlite"))
            bulk("WhatsApp Attachments", MatchFiles.WHATSAPP_ATTACHMENTS,
                 os.path.join(out, "whatsapp_attachments"), preserve_folders=False)
        if opts.get("voicemail"):
            bulk("Voicemail", MatchFiles.VOICEMAIL, os.path.join(out, "voicemail"))

        self.after(0, self._finish, all_ok)

    def _finish(self, ok):
        self._decrypt_btn.config(state="normal")
        self._val_btn.config(state="normal")
        if ok:
            self._prog_bar.config(value=100)
            self._prog_status.config(
                text=f"Done  ·  {self._done_files} files extracted", fg=SUCCESS)
            self._log_write(f"Done. {self._done_files} files saved to output folder.", "ok")
        else:
            self._prog_status.config(text="Finished with errors", fg=ERROR)
            self._log_write("Completed with errors.", "warn")

    def _log_write(self, msg, tag=""):
        self._log.config(state="normal")
        self._log.insert("end", msg + "\n", tag)
        self._log.see("end")
        self._log.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()