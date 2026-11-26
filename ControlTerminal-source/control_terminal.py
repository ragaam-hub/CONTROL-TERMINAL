# -*- coding: utf-8 -*-
"""
CONTROL TERMINAL - by JORE-boy.
"""
import random
import string
import tkinter as tk

# ================== SETTINGS ==================
PIN = "2580"            # change the PIN here
AUTO = True             # True = keep running scan/hack sessions automatically
FONT = ("Consolas", 13)
FG = "#00ff66"
FG_DIM = "#00a844"
FG_WARN = "#ffcc00"
FG_ERR = "#ff3355"
FG_CYAN = "#33e0ff"
BG = "#000000"
# =============================================


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


def rtarget():
    kind = random.random()
    if kind < 0.4:
        return rip()
    if kind < 0.7:
        return rhost()
    return random.choice(["mainframe", "gateway", "auth-core", "datavault", "node-cluster",
                          "root-dns", "backup-grid", "edge-relay"]) + "." + rhex(4)


class Terminal:
    def __init__(self, root):
        self.root = root
        self.busy = False
        self.queue = []
        self.history = []
        self.hidx = 0
        self.auto = AUTO

        root.title("CONTROL TERMINAL")
        root.configure(bg=BG)
        root.attributes("-fullscreen", True)
        root.attributes("-topmost", True)
        root.protocol("WM_DELETE_WINDOW", self.blocked)
        for seq in ("<Alt-F4>", "<Escape>", "<Control-w>", "<Control-q>"):
            root.bind_all(seq, lambda e: (self.blocked(), "break")[1])

        # output area (read-only)
        self.txt = tk.Text(root, bg=BG, fg=FG, font=FONT, bd=0, highlightthickness=0,
                           wrap="char", padx=16, pady=12)
        self.txt.pack(fill="both", expand=True)
        for tag, col in (("dim", FG_DIM), ("warn", FG_WARN), ("err", FG_ERR),
                         ("cyan", FG_CYAN), ("ok", FG)):
            self.txt.tag_config(tag, foreground=col)
        self.txt.configure(state="disabled")

        # command bar (always typable, even while the stream runs)
        bar = tk.Frame(root, bg=BG)
        bar.pack(fill="x", side="bottom")
        tk.Label(bar, text=" root@control:~# ", bg=BG, fg=FG_CYAN, font=FONT).pack(side="left")
        self.entry = tk.Entry(bar, bg=BG, fg=FG, insertbackground=FG, font=FONT,
                              bd=0, highlightthickness=0)
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Up>", self.hist_up)
        self.entry.bind("<Down>", self.hist_down)
        self.entry.focus_set()

        self.keep_on_top()
        self.boot()

    # ---------- window guard ----------
    def keep_on_top(self):
        try:
            self.root.attributes("-topmost", True)
            self.root.lift()
            self.entry.focus_force()
        except tk.TclError:
            return
        self.root.after(1500, self.keep_on_top)

    def blocked(self):
        self.write("\n[!] ACCESS DENIED - session locked.\n", "err")

    # ---------- output ----------
    def write(self, s, tag="ok"):
        self.txt.configure(state="normal")
        self.txt.insert("end", s, tag)
        lines = int(self.txt.index("end-1c").split(".")[0])
        if lines > 1500:
            self.txt.delete("1.0", f"{lines - 1200}.0")
        self.txt.see("end")
        self.txt.configure(state="disabled")

    # ---------- command bar ----------
    def on_enter(self, e):
        cmd = self.entry.get().strip()
        self.entry.delete(0, "end")
        if cmd:
            self.history.append(cmd)
        self.hidx = len(self.history)
        if cmd:
            self.write(f"\nroot@control:~# {cmd}\n", "cyan")
        self.run(cmd)
        return "break"

    def hist_up(self, e):
        if self.history:
            self.hidx = max(0, self.hidx - 1)
            self.entry.delete(0, "end")
            self.entry.insert(0, self.history[self.hidx])
        return "break"

    def hist_down(self, e):
        if self.history:
            self.hidx = min(len(self.history), self.hidx + 1)
            self.entry.delete(0, "end")
            if self.hidx < len(self.history):
                self.entry.insert(0, self.history[self.hidx])
        return "break"

    # ---------- animation scheduler ----------
    def add(self, fn, delay):
        self.queue.append((fn, delay))

    def line(self, s, tag="ok", delay=None):
        if delay is None:
            delay = random.randint(25, 180)
        self.add(lambda: self.write(s + "\n", tag), delay)

    def start(self):
        if self.busy:
            return
        self.busy = True
        self.step()

    def step(self):
        if not self.queue:
            self.busy = False
            self.after_queue()
            return
        fn, d = self.queue.pop(0)
        fn()
        try:
            self.root.after(d, self.step)
        except tk.TclError:
            pass

    def after_queue(self):
        if self.auto:
            self.root.after(random.randint(400, 1400), self.auto_session)

    def progress(self, label, tag="ok"):
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
                self.txt.configure(state="normal")
                self.txt.delete("pbar", "end-1c")
                self.txt.configure(state="disabled")
                self.write(b, "dim")
            self.add(draw, delay)
        self.add(lambda: self.write("  OK\n", "ok"), 120)

    def hexdump(self, n=None):
        for _ in range(n or random.randint(3, 9)):
            self.line(f"0x{rhex(8)}  " + " ".join(rhex(2) for _ in range(16)),
                      "dim", random.randint(15, 60))

    # ---------- action blocks ----------
    def b_scan(self, t):
        self.line(f"[*] Scanning ports on {t} ...", "cyan")
        for p in sorted(random.sample(range(20, 9000), random.randint(3, 7))):
            st = random.choice(["open", "open", "filtered", "closed"])
            self.line(f"    {p}/tcp  {st:<9} {random.choice(['ssh', 'http', 'https', 'smb', 'mysql', 'rdp', 'unknown'])}",
                      "ok" if st == "open" else "dim")

    def b_connect(self, t):
        self.line(f"[*] Connecting to {t}:{rport()} via {rhost()} ...", "cyan", 400)
        for _ in range(random.randint(1, 3)):
            self.line(f"    hop -> {rip()}  {random.randint(4, 220)}ms", "dim")
        if random.random() < 0.35:
            self.line("[-] Connection timed out, trying alternate route ...", "warn", 700)
        self.line(f"[+] Connected. Session ID {rhex(16)}", "ok", 300)

    def b_handshake(self, t):
        self.line(f"[*] TLS handshake {random.choice(['TLSv1.3', 'TLSv1.2'])} "
                  f"{random.choice(['AES-256-GCM', 'CHACHA20-POLY1305', 'AES-128-GCM'])}", "cyan")
        self.hexdump(random.randint(2, 5))
        self.line(f"[+] Session key: {rhex(32)}", "ok")

    def b_bypass(self, t):
        layer = random.choice(["firewall", "IDS", "WAF", "2FA gateway", "proxy auth", "rate limiter"])
        self.line(f"[*] Bypassing {layer} ...", "cyan")
        for i in range(random.randint(2, 5)):
            self.line(f"    payload #{i + 1} {rhex(10)} ->
