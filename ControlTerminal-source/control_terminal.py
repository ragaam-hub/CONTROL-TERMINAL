# -*- coding: utf-8 -*-
"""
CONTROL TERMINAL - simulated "hacking" screen for prank / fun.  by JORE-boy
Does nothing to the system: all output is fake and randomized.

Exit : type  unlock <PIN>  in the input bar (default PIN below).
Safe : Ctrl+Alt+Del -> Task Manager still works, so you are never truly locked out.
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
        self.write("\n[!] ACCESS DENIED - session locked. Type 'unlock <PIN>' in the bar below.\n", "err")

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
    SERVICES = ["ssh", "http", "https", "smb", "mysql", "rdp", "unknown"]

    def b_scan(self, t):
        self.line(f"[*] Scanning ports on {t} ...", "cyan")
        for p in sorted(random.sample(range(20, 9000), random.randint(3, 7))):
            st = random.choice(["open", "open", "filtered", "closed"])
            svc = random.choice(self.SERVICES)
            tag = "ok" if st == "open" else "dim"
            self.line(f"    {p}/tcp  {st:<9} {svc}", tag)

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
            res = random.choice(["blocked", "blocked", "passed"])
            self.line(f"    payload #{i + 1} {rhex(10)} -> {res}", "dim", random.randint(120, 400))
        self.line(f"[+] {layer} bypassed", "ok", 300)

    def b_bruteforce(self, t):
        user = random.choice(["admin", "root", "operator", "user01", "sysadmin", str(t).split('.')[0]])
        self.line(f"[*] Brute-forcing login '{user}' ...", "cyan")
        for _ in range(random.randint(6, 16)):
            pw = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(6, 12)))
            self.line(f"    try {pw:<14} FAIL", "dim", random.randint(20, 70))
        self.line(f"[+] Password matched: {'*' * random.randint(8, 12)}", "ok", 400)

    def b_download(self, t):
        self.line(f"[*] Downloading data from {t} ...", "cyan")
        for _ in range(random.randint(1, 3)):
            self.progress(f"    > {rfile()} ({rsize()})")

    def b_upload(self, t):
        self.progress(f"[*] Uploading module {rfile()} to /tmp/.{rhex(6)}", "cyan")

    def b_decrypt(self, t):
        self.line(f"[*] Decrypting {rfile()} ...", "cyan")
        for _ in range(random.randint(3, 7)):
            self.line(f"    block {rhex(4)}: {rhex(24)}", "dim", random.randint(40, 120))
        self.line("[+] Decryption complete", "ok")

    def b_users(self, t):
        self.line("[*] Dumping user table ...", "cyan")
        names = ["andi", "budi", "sari", "rina", "dimas", "eka", "fajar", "gita", "hendra", "intan", "joko", "lina"]
        for n in random.sample(names, random.randint(3, 6)):
            uid = random.randint(1000, 9999)
            day = random.randint(1, 28)
            hh = random.randint(0, 23)
            mm = random.randint(0, 59)
            self.line(f"    uid={uid:<5} {n:<8} last={day:02d}/11 {hh:02d}:{mm:02d}  mac={rmac()}", "dim")

    def b_inject(self, t):
        self.line(f"[*] Injecting process PID {random.randint(300, 9999)} ...", "cyan", 300)
        self.hexdump()
        self.line("[+] Shell active", "ok")

    def b_clean(self, t):
        self.line("[*] Wiping log trails ...", "cyan")
        for f in ["auth.log", "syslog", "access.log", "events.evtx", "history"]:
            if random.random() < 0.7:
                self.line(f"    rm -f /var/log/{f}  ... done", "dim", random.randint(60, 200))

    BLOCKS = ["b_scan", "b_handshake", "b_bypass", "b_bruteforce", "b_download", "b_upload",
              "b_decrypt", "b_users", "b_inject"]

    # ---------- boot ----------
    def boot(self):
        art = r"""
   ____ ___  _   _ _____ ____   ___  _
  / ___/ _ \| \ | |_   _|  _ \ / _ \| |
 | |  | | | |  \| | | | | |_) | | | | |
 | |__| |_| | |\  | | | |  _ <| |_| | |___
  \____\___/|_| \_| |_| |_| \_\\___/|_____|
            T E R M I N A L           by JORE-boy
"""
        self.line(art, "ok", 300)
        for s in ["Loading kernel modules", "Mounting encrypted volume", "Starting network daemon",
                  "Spoofing MAC address", "Routing via TOR relays"]:
            self.line(f"[ OK ] {s}" + ("." * random.randint(3, 12)), "dim", random.randint(80, 350))
        self.line("\nSYSTEM LOCKED. Type 'unlock <PIN>' below to release. Type 'help' for commands.", "warn", 100)
        self.start()

    # ---------- auto stream ----------
    def auto_session(self):
        if self.busy:
            return
        kind = random.random()
        if kind < 0.3:
            self.do_scan(rtarget(), announce=True)
        elif kind < 0.45:
            self.line(f"[~] Monitoring node {rhost()} ... {random.randint(2, 40)} active sessions", "dim", 200)
            self.line(f"    inbound {rip()} -> {rport()}   {rsize()}/s", "dim", 150)
        else:
            self.do_hack(rtarget())
        self.start()

    def do_scan(self, target, announce=False):
        if announce:
            self.line(f"\n[sweep {rhex(4).upper()}] range {rip()}/{random.choice([16, 20, 24])}", "warn", 200)
        self.b_scan(target)

    def do_hack(self, target):
        self.line(f"\n=== OPERATION {rhex(6).upper()} :: target {target} ===", "warn", 300)
        self.line(f"[*] Resolving {target} -> {rip()}", "cyan")
        self.b_connect(target)
        blocks = random.sample(self.BLOCKS, random.randint(4, 7))
        if "b_download" not in blocks:
            blocks.insert(random.randint(1, len(blocks)), "b_download")
        for b in blocks:
            getattr(self, b)(target)
        if random.random() < 0.6:
            self.b_clean(target)
        total = random.randint(40, 2600)
        self.line(f"\n[OK] DONE in {random.uniform(8, 95):.1f}s  |  {total} files  |  "
                  f"{random.uniform(0.2, 14):.2f} GB exfiltrated", "ok", 300)
        self.line(f"[OK] Root access to {target} saved as session #{random.randint(100, 999)}", "ok")

    def matrix(self):
        for _ in range(random.randint(40, 70)):
            row = "".join(random.choice("01$#@%&") if random.random() < 0.55 else " " for _ in range(90))
            self.line(row, random.choice(["ok", "dim"]), 35)

    # ---------- commands ----------
    def run(self, raw):
        parts = raw.split()
        if not parts:
            self.start()
            return
        cmd, args = parts[0].lower(), parts[1:]

        if cmd == "unlock":
            if args and args[0] == PIN:
                self.auto = False
                self.queue = []
                self.write("\n[+] PIN accepted. Closing session ...\n", "ok")
                self.root.after(600, self.root.destroy)
                return
            else:
                self.line("[!] WRONG PIN. Attempt logged.", "err", 300)
        elif cmd == "help":
            for s in ["  hack <target>   run an attack session",
                      "  scan <target>   scan ports",
                      "  download        pull random data",
                      "  matrix          code-rain effect",
                      "  whoami          session info",
                      "  auto on|off     toggle the automatic stream",
                      "  clear           clear the screen",
                      "  unlock <PIN>    unlock & exit"]:
                self.line(s, "dim", 30)
        elif cmd in ("exit", "quit", "logout", "close"):
            self.line("[!] Cannot exit. Use 'unlock <PIN>'.", "err")
        elif cmd == "auto":
            self.auto = bool(args and args[0] == "on")
            self.line(f"[+] auto stream {'ON' if self.auto else 'OFF'}", "ok")
        elif cmd == "clear":
            self.txt.configure(state="normal")
            self.txt.delete("1.0", "end")
            self.txt.configure(state="disabled")
        elif cmd == "whoami":
            self.line(f"root  (uid=0)  host=control-{rhex(4)}  ip={rip()}  vpn={rhost()}", "dim")
        elif cmd == "scan":
            self.do_scan(args[0] if args else rtarget(), announce=True)
        elif cmd == "download":
            self.b_download(rhost())
        elif cmd == "matrix":
            self.matrix()
        elif cmd == "hack":
            self.do_hack(" ".join(args) if args else rtarget())
        else:
            self.line(f"bash: {cmd}: command not found", "err", 50)
        self.start()


if __name__ == "__main__":
    root = tk.Tk()
    Terminal(root)
    root.mainloop()
