# -*- coding: utf-8 -*-
"""
CONTROL TERMINAL - simulasi "hacking" untuk prank / hiburan.  by 17
Tidak melakukan apa pun ke sistem: semua output palsu & acak.

Keluar : ketik  unlock <PIN>   (PIN default ada di bawah)
Darurat: Ctrl+Alt+Del -> Task Manager tetap berfungsi.
"""
import random
import string
import tkinter as tk
import time

# ================== PENGATURAN ==================
PIN = "2580"            # ganti PIN sesukamu
FONT = ("Consolas", 13)
FG = "#00ff66"
FG_DIM = "#00a844"
FG_WARN = "#ffcc00"
FG_ERR = "#ff3355"
FG_CYAN = "#33e0ff"
BG = "#000000"
# ================================================


def rhex(n):
    return "".join(random.choice("0123456789abcdef") for _ in range(n))


def rip():
    return ".".join(str(random.randint(11, 254)) for _ in range(4))


def rport():
    return random.choice([21, 22, 23, 80, 443, 445, 3306, 3389, 5432, 8080, 8443, random.randint(1024, 65535)])


def rmac():
    return ":".join(rhex(2) for _ in range(6))


def rfile():
    names = ["config", "backup", "user_db", "session", "cache", "keystore", "payload", "dump",
             "auth", "token", "core", "sys", "kernel", "mod", "net", "shadow", "log", "vault"]
    exts = [".bin", ".dat", ".db", ".enc", ".sys", ".tmp", ".pak", ".log", ".json", ".img"]
    return random.choice(names) + "_" + rhex(random.randint(3, 6)) + random.choice(exts)


def rhost():
    a = ["node", "srv", "gw", "core", "edge", "relay", "db", "proxy", "mx", "vpn"]
    b = ["jkt", "sgp", "tyo", "fra", "ams", "nyc", "bgr", "sby", "lon", "hkg"]
    return f"{random.choice(a)}-{random.randint(1, 99):02d}.{random.choice(b)}.{rhex(4)}.net"


def rsize():
    v = random.uniform(0.3, 980)
    return f"{v:.1f} {random.choice(['KB', 'MB', 'MB', 'GB'])}"


class Terminal:
    def __init__(self, root):
        self.root = root
        self.busy = False
        self.queue = []          # antrian (fungsi, delay_ms)
        self.history = []
        self.hidx = 0

        root.title("CONTROL TERMINAL")
        root.configure(bg=BG)
        root.attributes("-fullscreen", True)
        root.attributes("-topmost", True)
        root.protocol("WM_DELETE_WINDOW", self.blocked)   # tombol X diabaikan
        for seq in ("<Alt-F4>", "<Escape>", "<Control-w>", "<Control-q>"):
            root.bind_all(seq, lambda e: (self.blocked(), "break")[1])

        self.txt = tk.Text(root, bg=BG, fg=FG, insertbackground=FG, font=FONT,
                           bd=0, highlightthickness=0, wrap="char", padx=16, pady=12)
        self.txt.pack(fill="both", expand=True)
        for tag, col in (("dim", FG_DIM), ("warn", FG_WARN), ("err", FG_ERR),
                         ("cyan", FG_CYAN), ("ok", FG)):
            self.txt.tag_config(tag, foreground=col)

        self.txt.bind("<Key>", self.on_key)
        self.txt.bind("<Return>", self.on_enter)
        self.txt.bind("<BackSpace>", self.on_back)
        self.txt.bind("<Up>", self.hist_up)
        self.txt.bind("<Down>", self.hist_down)
        self.txt.bind("<Button-1>", lambda e: (self.txt.focus_set(), "break")[1])
        self.txt.focus_set()

        self.keep_on_top()
        self.boot()

    # ---------- penjaga jendela ----------
    def keep_on_top(self):
        try:
            self.root.attributes("-topmost", True)
            self.root.lift()
            if not self.busy:
                self.txt.focus_force()
        except tk.TclError:
            return
        self.root.after(1500, self.keep_on_top)

    def blocked(self):
        if not self.busy:
            self.write("\n[!] ACCESS DENIED - sesi terkunci. Ketik 'unlock <PIN>'.\n", "err")
            self.prompt()

    # ---------- output ----------
    def write(self, s, tag="ok"):
        self.txt.insert("end", s, tag)
        self.txt.see("end")
        lines = int(self.txt.index("end-1c").split(".")[0])
        if lines > 1500:
            self.txt.delete("1.0", f"{lines - 1200}.0")

    def prompt(self):
        self.write(f"\nroot@control-{rhex(4)}:~# ", "cyan")
        self.txt.mark_set("input_start", "end-1c")
        self.txt.mark_gravity("input_start", "left")
        self.txt.mark_set("insert", "end")

    # ---------- input ----------
    def on_key(self, e):
        if self.busy:
            return "break"
        if e.keysym in ("Left", "Right", "Home", "End"):
            return None
        if self.txt.compare("insert", "<", "input_start"):
            self.txt.mark_set("insert", "end")

    def on_back(self, e):
        if self.busy or self.txt.compare("insert", "<=", "input_start"):
            return "break"

    def on_enter(self, e):
        if self.busy:
            return "break"
        cmd = self.txt.get("input_start", "end-1c").strip()
        self.write("\n")
        if cmd:
            self.history.append(cmd)
        self.hidx = len(self.history)
        self.run(cmd)
        return "break"

    def set_input(self, s):
        self.txt.delete("input_start", "end-1c")
        self.txt.insert("end", s, "ok")

    def hist_up(self, e):
        if self.history and not self.busy:
            self.hidx = max(0, self.hidx - 1)
            self.set_input(self.history[self.hidx])
        return "break"

    def hist_down(self, e):
        if self.history and not self.busy:
            self.hidx = min(len(self.history), self.hidx + 1)
            self.set_input(self.history[self.hidx] if self.hidx < len(self.history) else "")
        return "break"

    # ---------- penjadwal animasi ----------
    def add(self, fn, delay):
        self.queue.append((fn, delay))

    def line(self, s, tag="ok", delay=None):
        if delay is None:
            delay = random.randint(25, 180)
        self.add(lambda: self.write(s + "\n", tag), delay)

    def start(self):
        self.busy = True
        self.step()

    def step(self):
        if not self.queue:
            self.busy = False
            self.prompt()
            return
        fn, d = self.queue.pop(0)
        fn()
        try:
            self.root.after(d, self.step)
        except tk.TclError:
            pass  # jendela sudah ditutup (unlock)

    def progress(self, label, tag="ok"):
        """Progress bar dengan kecepatan tidak rata (kadang macet, kadang ngebut)."""
        width = 34
        pct = 0
        self.add(lambda: self.write(f"{label}\n", tag), 60)
        self.add(lambda: self.txt.mark_set("pbar", "end-1c") or
                 self.txt.mark_gravity("pbar", "left"), 0)
        while pct < 100:
            pct = min(100, pct + random.choice([1, 1, 2, 3, 4, 7, 11, 0]))
            delay = random.choice([30, 40, 60, 90, 140, 400]) if pct < 100 else 200
            fill = int(width * pct / 100)
            spd = f"{random.uniform(0.4, 48):.1f} MB/s"
            bar = f"  [{'#' * fill}{'.' * (width - fill)}] {pct:3d}%  {spd}"

            def draw(b=bar):
                self.txt.delete("pbar", "end-1c")
                self.write(b, "dim")
            self.add(draw, delay)
        self.add(lambda: self.write("  OK\n", "ok"), 120)

    def hexdump(self, n=None):
        for _ in range(n or random.randint(3, 9)):
            addr = f"0x{rhex(8)}"
            data = " ".join(rhex(2) for _ in range(16))
            self.line(f"{addr}  {data}", "dim", random.randint(15, 60))

    # ---------- blok-blok aksi (diacak urutannya) ----------
    def b_scan(self, t):
        self.line(f"[*] Memindai port {t} ...", "cyan")
        for p in sorted(random.sample(range(20, 9000), random.randint(3, 7))):
            st = random.choice(["open", "open", "filtered", "closed"])
            self.line(f"    {p}/tcp  {st:<9} {random.choice(['ssh', 'http', 'https', 'smb', 'mysql', 'rdp', 'unknown'])}",
                      "ok" if st == "open" else "dim")

    def b_connect(self, t):
        self.line(f"[*] Menyambungkan ke {t}:{rport()} via {rhost()} ...", "cyan", 400)
        for _ in range(random.randint(1, 3)):
            self.line(f"    hop -> {rip()}  {random.randint(4, 220)}ms", "dim")
        if random.random() < 0.35:
            self.line("[-] Koneksi timeout, mencoba rute alternatif ...", "warn", 700)
        self.line(f"[+] Terhubung. Session ID {rhex(16)}", "ok", 300)

    def b_handshake(self, t):
        self.line(f"[*] TLS handshake {random.choice(['TLSv1.3', 'TLSv1.2'])} "
                  f"{random.choice(['AES-256-GCM', 'CHACHA20-POLY1305', 'AES-128-GCM'])}", "cyan")
        self.hexdump(random.randint(2, 5))
        self.line(f"[+] Kunci sesi: {rhex(32)}", "ok")

    def b_bypass(self, t):
        layer = random.choice(["firewall", "IDS", "WAF", "2FA gateway", "proxy auth", "rate limiter"])
        self.line(f"[*] Bypass {layer} ...", "cyan")
        for i in range(random.randint(2, 5)):
            self.line(f"    payload #{i + 1} {rhex(10)} -> {random.choice(['ditolak', 'ditolak', 'lolos'])}",
                      "dim", random.randint(120, 400))
        self.line(f"[+] {layer} berhasil dilewati", "ok", 300)

    def b_bruteforce(self, t):
        user = random.choice(["admin", "root", "operator", "user01", "sysadmin", t.split('.')[0]])
        self.line(f"[*] Brute-force login '{user}' ...", "cyan")
        for _ in range(random.randint(6, 16)):
            pw = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(6, 12)))
            self.line(f"    try {pw:<14} FAIL", "dim", random.randint(20, 70))
        self.line(f"[+] Password cocok: {'*' * random.randint(8, 12)}", "ok", 400)

    def b_download(self, t):
        self.line(f"[*] Mengunduh data dari {t} ...", "cyan")
        for _ in range(random.randint(1, 3)):
            self.progress(f"    > {rfile()} ({rsize()})")

    def b_upload(self, t):
        self.progress(f"[*] Mengunggah modul {rfile()} ke /tmp/.{rhex(6)}", "cyan")

    def b_decrypt(self, t):
        self.line(f"[*] Mendekripsi {rfile()} ...", "cyan")
        for _ in range(random.randint(3, 7)):
            self.line(f"    block {rhex(4)}: {rhex(24)}", "dim", random.randint(40, 120))
        self.line("[+] Dekripsi selesai", "ok")

    def b_users(self, t):
        self.line("[*] Mengambil daftar user ...", "cyan")
        names = ["andi", "budi", "sari", "rina", "dimas", "eka", "fajar", "gita", "hendra", "intan", "joko", "lina"]
        for n in random.sample(names, random.randint(3, 6)):
            self.line(f"    uid={random.randint(1000, 9999):<5} {n:<8} last_login={random.randint(1, 28):02d}/11 "
                      f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}  mac={rmac()}", "dim")

    def b_inject(self, t):
        self.line(f"[*] Inject proses PID {random.randint(300, 9999)} ...", "cyan", 300)
        self.hexdump()
        self.line("[+] Shell aktif", "ok")

    def b_clean(self, t):
        self.line("[*] Menghapus jejak log ...", "cyan")
        for f in ["auth.log", "syslog", "access.log", "events.evtx", "history"]:
            if random.random() < 0.7:
                self.line(f"    rm -f /var/log/{f}  ... done", "dim", random.randint(60, 200))

    BLOCKS = ["b_scan", "b_handshake", "b_bypass", "b_bruteforce", "b_download", "b_upload",
              "b_decrypt", "b_users", "b_inject"]

    # ---------- perintah ----------
    def boot(self):
        art = r"""
   ____ ___  _   _ _____ ____   ___  _
  / ___/ _ \| \ | |_   _|  _ \ / _ \| |
 | |  | | | |  \| | | | | |_) | | | | |
 | |__| |_| | |\  | | | |  _ <| |_| | |___
  \____\___/|_| \_| |_| |_| \_\\___/|_____|
            T E R M I N A L           by 17
"""
        self.line(art, "ok", 300)
        for s in ["Loading kernel modules", "Mounting encrypted volume", "Starting network daemon",
                  "Spoofing MAC address", "Routing via TOR relays"]:
            self.line(f"[ OK ] {s}" + ("." * random.randint(3, 12)), "dim", random.randint(80, 350))
        self.line("\nSesi TERKUNCI. Ketik 'help' untuk daftar perintah.", "warn", 100)
        self.start()

    def run(self, raw):
        parts = raw.split()
        if not parts:
            self.prompt()
            return
        cmd, args = parts[0].lower(), parts[1:]

        if cmd == "help":
            for s in ["  hack <target>   jalankan serangan (target bebas: ip / nama / domain)",
                      "  scan <target>   pindai port",
                      "  download        unduh data acak",
                      "  matrix          efek hujan kode",
                      "  whoami          info sesi",
                      "  clear           bersihkan layar",
                      "  unlock <PIN>    buka kunci & keluar"]:
                self.line(s, "dim", 30)
        elif cmd == "unlock":
            if args and args[0] == PIN:
                self.line("[+] PIN benar. Menutup sesi ...", "ok", 900)
                self.add(self.root.destroy, 0)
            else:
                self.line("[!] PIN SALAH. Percobaan dicatat.", "err", 300)
        elif cmd in ("exit", "quit", "logout", "close"):
            self.line("[!] Tidak bisa keluar. Gunakan 'unlock <PIN>'.", "err")
        elif cmd == "clear":
            self.txt.delete("1.0", "end")
        elif cmd == "whoami":
            self.line(f"root  (uid=0)  host=control-{rhex(4)}  ip={rip()}  vpn={rhost()}", "dim")
        elif cmd == "scan":
            self.b_scan(args[0] if args else rip())
        elif cmd == "download":
            self.b_download(rhost())
        elif cmd == "matrix":
            self.matrix()
        elif cmd == "hack":
            self.hack(" ".join(args) if args else rip())
        else:
            self.line(f"bash: {cmd}: command not found", "err", 50)
        self.start()

    def hack(self, target):
        self.line(f"\n=== OPERASI {rhex(6).upper()} :: target {target} ===", "warn", 300)
        self.line(f"[*] Resolve {target} -> {rip()}", "cyan")
        self.b_connect(target)
        # pilih & acak blok supaya tiap run beda
        blocks = random.sample(self.BLOCKS, random.randint(4, 7))
        if "b_download" not in blocks:
            blocks.insert(random.randint(1, len(blocks)), "b_download")
        for b in blocks:
            getattr(self, b)(target)
        if random.random() < 0.6:
            self.b_clean(target)
        total = random.randint(40, 2600)
        self.line(f"\n[✓] SELESAI dalam {random.uniform(8, 95):.1f}s  |  {total} file  |  "
                  f"{random.uniform(0.2, 14):.2f} GB diambil", "ok", 300)
        self.line(f"[✓] Akses root ke {target} tersimpan sebagai sesi #{random.randint(100, 999)}", "ok")

    def matrix(self):
        cols = 90
        for _ in range(random.randint(40, 70)):
            row = "".join(random.choice("01アイウエオカキクケコ$#@%&") if random.random() < 0.55 else " "
                          for _ in range(cols))
            self.line(row, random.choice(["ok", "dim"]), 35)


if __name__ == "__main__":
    root = tk.Tk()
    Terminal(root)
    root.mainloop()
