"""
CPU Scheduling Algorithms Simulator — GUI Edition
Tkinter-based GUI with Gantt chart canvas, results table, and stats panel.
Algorithms: FCFS, SJF, SRT, Round Robin, Priority (NP), Priority + RR
"""

import copy
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

# ─────────────────────────────────────────────
#  Palette
# ─────────────────────────────────────────────
BG        = "#1B211A"  # deep forest charcoal (your base)
PANEL     = "#232C22"  # lifted moss-dark panel
CARD      = "#2C3A2B"  # soft green-gray surface
BORDER    = "#3E4A3A"  # muted leaf steel border

ACCENT    = "#628141"  # primary moss green accent
ACCENT2   = "#8BAE66"  # lighter leaf highlight

TEXT      = "#EBD5AB"  # warm sand text (soft contrast, not pure white)
MUTED     = "#A8B39A"  # foggy green-gray text

ERROR     = "#C96A5B"  # muted rust red
WARNING   = "#C2A25A"  # aged gold
SUCCESS   = "#7FAE7A"  # natural green success

PROC_COLORS = [
    "#8b93a7",  # steel blue-gray
    "#7fbf9b",  # muted mint
    "#d46a6a",  # soft rust red
    "#c9a66b",  # antique gold
    "#a7b3c6",  # pale fog blue-gray
    "#89a7c7",  # cool slate blue
    "#c58c7a",  # muted clay orange
    "#b46b7a",  # dusty rose red
    "#7a8fb5",  # washed indigo
    "#b39ddb",  # fog violet
    "#9ccc65",  # softened green
    "#64b5f6",  # muted sky blue
    "#f48fb1",  # faded pink
    "#ce93d8",  # soft lavender
    "#80cbc4",  # pale teal
]


# algorithm logic / solving
def reset(processes):
    procs = copy.deepcopy(processes)
    for p in procs:
        p["remaining"] = p["bt"]
        p["finish"] = 0
        p["start"] = -1
    return procs

def compute_times(processes):
    results = []
    for p in processes:
        tat = p["finish"] - p["at"]
        wt  = tat - p["bt"]
        results.append({**p, "tat": tat, "wt": wt})
    return results

def run_fcfs(processes):
    procs = sorted(reset(processes), key=lambda p: (p["at"], int(p["pid"][1:])))
    time, gantt = 0, []
    for p in procs:
        if time < p["at"]: time = p["at"]
        p["start"] = time
        time += p["bt"]
        p["finish"] = time
        gantt.append({"pid": p["pid"], "start": time - p["bt"], "end": time})
    return gantt, compute_times(procs)

def run_sjf(processes):
    procs, done, gantt, time = reset(processes), [], [], 0
    remaining = procs[:]
    while remaining:
        avail = [p for p in remaining if p["at"] <= time]
        if not avail:
            time = min(p["at"] for p in remaining); continue
        p = min(avail, key=lambda x: (x["bt"], x["at"], x["pid"]))
        remaining.remove(p)
        p["start"] = time
        gantt.append({"pid": p["pid"], "start": time, "end": time + p["bt"]})
        time += p["bt"]; p["finish"] = time; done.append(p)
    return gantt, compute_times(done)

def run_srt(processes):
    procs = reset(processes)
    n, time, done, gantt = len(procs), 0, 0, []
    while done < n:
        avail = [p for p in procs if p["at"] <= time and p["remaining"] > 0]
        if not avail: time += 1; continue
        p = min(avail, key=lambda x: (x["remaining"], x["at"], x["pid"]))
        if p["start"] == -1: p["start"] = time
        if gantt and gantt[-1]["pid"] == p["pid"]:
            gantt[-1]["end"] = time + 1
        else:
            gantt.append({"pid": p["pid"], "start": time, "end": time + 1})
        p["remaining"] -= 1; time += 1
        if p["remaining"] == 0:
            p["finish"] = time; done += 1
    return gantt, compute_times(procs)

def run_rr(processes, quantum):
    procs   = reset(processes)
    procs_s = sorted(procs, key=lambda p: p["at"])
    queue, gantt, time, arrived = [], [], 0, set()
    idx, n, done = 0, len(procs_s), 0
    while idx < n and procs_s[idx]["at"] <= time:
        queue.append(procs_s[idx]); arrived.add(procs_s[idx]["pid"]); idx += 1
    while done < n:
        if not queue:
            time = procs_s[idx]["at"]
            while idx < n and procs_s[idx]["at"] <= time:
                queue.append(procs_s[idx]); arrived.add(procs_s[idx]["pid"]); idx += 1
        p = queue.pop(0)
        if p["start"] == -1: p["start"] = time
        run = min(quantum, p["remaining"])
        gantt.append({"pid": p["pid"], "start": time, "end": time + run})
        time += run; p["remaining"] -= run
        while idx < n and procs_s[idx]["at"] <= time:
            queue.append(procs_s[idx]); arrived.add(procs_s[idx]["pid"]); idx += 1
        if p["remaining"] > 0: queue.append(p)
        else: p["finish"] = time; done += 1
    return gantt, compute_times(procs)

def run_priority_np(processes, higher_is_better):
    procs, done, gantt, time = reset(processes), [], [], 0
    remaining = procs[:]
    sign = -1 if higher_is_better else 1
    while remaining:
        avail = [p for p in remaining if p["at"] <= time]
        if not avail: time = min(p["at"] for p in remaining); continue
        p = min(avail, key=lambda x: (sign * x["priority"], x["at"], x["pid"]))
        remaining.remove(p); p["start"] = time
        gantt.append({"pid": p["pid"], "start": time, "end": time + p["bt"]})
        time += p["bt"]; p["finish"] = time; done.append(p)
    return gantt, compute_times(done)

def run_priority_rr(processes, quantum, higher_is_better):
    procs  = reset(processes)
    sign   = -1 if higher_is_better else 1
    procs_s = sorted(procs, key=lambda p: (p["at"], sign * p["priority"]))
    queue, gantt, time = [], [], 0
    idx, n, done = 0, len(procs_s), 0
    def enqueue():
        nonlocal idx
        while idx < n and procs_s[idx]["at"] <= time:
            queue.append(procs_s[idx]); idx += 1
        queue.sort(key=lambda x: (sign * x["priority"], x["at"]))
    enqueue()
    while done < n:
        if not queue: time = procs_s[idx]["at"]; enqueue()
        p = queue.pop(0)
        if p["start"] == -1: p["start"] = time
        run = min(quantum, p["remaining"])
        gantt.append({"pid": p["pid"], "start": time, "end": time + run})
        time += run; p["remaining"] -= run; enqueue()
        if p["remaining"] > 0:
            queue.append(p); queue.sort(key=lambda x: (sign * x["priority"], x["at"]))
        else: p["finish"] = time; done += 1
    return gantt, compute_times(procs)
# end of algorithm logic / solving



# utility functions
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text   = text
        self.tip    = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget,"bbox") else (0,0,0,0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(tw, text=self.text, background="#2e3250", foreground=TEXT,
                       relief="flat", padx=8, pady=4,
                       font=("Consolas", 9))
        lbl.pack()

    def hide(self, _=None):
        if self.tip: self.tip.destroy(); self.tip = None
        
    
# end of utility functions

# main application
class CPUSchedulerApp(tk.Tk):
    def __init__(self):
        #gui initialization
        super().__init__()
        self.title("CPU Scheduling Simulator")
        self.configure(bg=BG)
        self.geometry("1200x820")
        self.minsize(950, 650)
        self.resizable(True, True)

        # state initialization
        self.processes   = []
        self.proc_rows   = []   # list of (pid_var, at_var, bt_var, pri_var) per row
        self.color_map   = {}

        self._setup_styles() # set up general styles
        self._build_ui() # build ui
        
        

    # general styles
    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=TEXT, borderwidth=0)
        style.configure("TFrame",     background=BG)
        style.configure("Card.TFrame",background=CARD, relief="flat")
        style.configure("TLabel",     background=BG, foreground=TEXT,
                        font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=TEXT,
                        font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel",   background=BG, foreground=MUTED,
                        font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background=CARD, foreground=TEXT,
                        font=("Segoe UI", 11, "bold"))
        style.configure("Card.TLabel",  background=CARD, foreground=TEXT,
                        font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED,
                        font=("Segoe UI", 9))
        style.configure("Stat.TLabel",  background=CARD, foreground=ACCENT2,
                        font=("Segoe UI", 16, "bold"))
        style.configure("StatSub.TLabel",background=CARD, foreground=MUTED,
                        font=("Segoe UI", 8))
        style.configure("TCombobox", fieldbackground=PANEL, background=PANEL,
                        foreground=TEXT, selectbackground=ACCENT,
                        arrowcolor=MUTED)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL)])
        style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT,
                        insertcolor=TEXT, borderwidth=1, relief="flat")
        style.configure("TSpinbox", fieldbackground=PANEL, foreground=TEXT,
                        arrowcolor=MUTED, borderwidth=0)
        style.configure("Treeview", background=PANEL, foreground=TEXT,
                        fieldbackground=PANEL, rowheight=28,
                        font=("Consolas", 10))
        style.configure("Treeview.Heading", background=CARD,
                        foreground=MUTED, font=("Segoe UI", 9, "bold"),
                        relief="flat")
        style.map("Treeview", background=[("selected", ACCENT)])
        style.configure("Vertical.TScrollbar", background=PANEL,
                        troughcolor=BG, arrowcolor=MUTED)
        style.configure("Horizontal.TScrollbar", background=PANEL,
                        troughcolor=BG, arrowcolor=MUTED)

    # ui styles
    def _build_ui(self):
       # ── Header ──
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(16, 0))
 
        # Left: title
        title_block = tk.Frame(header, bg=BG)
        title_block.pack(side="left")
        tk.Label(title_block, text="⚙  CPU Scheduling Simulator",
                 bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(title_block, text="OS Process Management",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(10, 0), pady=(5, 0))
 
        # Right: algorithm selector + options + run button
        ctrl = tk.Frame(header, bg=BG)
        ctrl.pack(side="right")
        
        # Run button
        tk.Button(ctrl, text="▶  Run",
                  bg=ACCENT, fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2",
                  activebackground="#5a52d5",
                  activeforeground="white",
                  padx=14, pady=6,
                  command=self._run_simulation).pack(side="left", padx=(8, 0))
 
                
      

        # divider / line
        # tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(10, 0))

        # ── Main pane ──
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=24, pady=16)
        main.columnconfigure(0, weight=0, minsize=320)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._build_left(main)
        self._build_right(main)

    # left side of ui
    def _build_left(self, parent):
        left = tk.Frame(parent, bg=BG )
        left.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        # ================= HEADER =================
        header = tk.Frame(left, bg=BG)
        header.pack(fill="x", pady=(16, 0))

        # LEFT side (title)
        title_left = tk.Frame(header, bg=BG)
        title_left.pack(side="left")

        tk.Label(
            title_left,
            text="PROCESSES", fg=MUTED,
            font=("Segoe UI", 8, "bold"), bg=BG
        ).pack(side="left")

        # RIGHT side (buttons)
        button_right = tk.Frame(header, bg=BG)
        button_right.pack(side="right")

        btn_row = tk.Frame(button_right, bg=BG)
        btn_row.pack()

        
        self._flat_btn(btn_row, "ADD PROCESS", self._add_process_row,
                    fg=ACCENT2, bg=ACCENT).pack(side="left")


        self._flat_btn(btn_row, "CLEAR VALUES", self._clear_all_process,
                    fg=ACCENT).pack(side="left", padx=(10, 0))
        
        self._flat_btn(btn_row, "RESET", self._reset_processes,
                    fg=ERROR).pack(side="left", padx=(8, 0))
        
        

        
        # ================= PROCESS TABLE =================
        
        #main card for process / outer div
        proc_card = tk.Frame(left, bg=ACCENT, bd=0)
        proc_card.pack(fill="x", pady=10)

        # container inside main card 
        hdr = tk.Frame(proc_card, bg=CARD)
        hdr.pack(fill="x", padx=70, pady=10)
        for col, w, txt in [("PID",7,"PID"),("Arrival Time",10,"Arrival Time"),("Burst Time",10,"Burst Time"),("Priority",10,"Priority"),("",3,"")]:
            tk.Label(hdr, text=txt, bg=CARD, fg=MUTED,
                     font=("Segoe UI", 8, "bold"), width=w, anchor="center").pack(side="left")  # CONTAINER FOR LABELS (PROCESS)

        # Scrollable process rows — canvas + scrollbar
        
        scroll_container = tk.Frame(proc_card, bg=CARD) # MAIN CONTAINER FOR scrollable area in PROCESS
        scroll_container.pack(fill="x", padx=10, pady=(0, 10))

        self._proc_canvas = tk.Canvas(scroll_container, bg=ACCENT,
                                      highlightthickness=0, height=120) # CANVAS INSIDE MAIN CONTAINER (SCROLLABLE ARE)
        self._proc_canvas.pack(side="left", fill="x", expand=True,  padx=(50, 0))

        proc_vsb = ttk.Scrollbar(scroll_container, orient="vertical",
                                  command=self._proc_canvas.yview)   # SCROLLBAR
        proc_vsb.pack(side="right", fill="y")
        self._proc_canvas.configure(yscrollcommand=proc_vsb.set)

        self.proc_frame = tk.Frame(self._proc_canvas, bg=CARD)
        self._proc_canvas_window = self._proc_canvas.create_window(
            (0, 0), window=self.proc_frame, anchor="nw"
        )

        def _on_proc_frame_configure(e):            # resize the height canvas when adding process (max height of 250)
            self._proc_canvas.configure(scrollregion=self._proc_canvas.bbox("all"))
            row_h = self.proc_frame.winfo_reqheight()     
            self._proc_canvas.configure(height=min(row_h, 310))

        def _on_proc_canvas_configure(e):
            self._proc_canvas.itemconfig(self._proc_canvas_window, width=e.width) # resize the width of canvas

        def _on_mousewheel(e):
            self._proc_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        # binders
        self.proc_frame.bind("<Configure>", _on_proc_frame_configure)
        self._proc_canvas.bind("<Configure>", _on_proc_canvas_configure)
        self._proc_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.proc_frame.bind("<MouseWheel>", _on_mousewheel)

        self._add_process_row()
        self._add_process_row()
        self._add_process_row()


        # ── Algorithm ──
        self._section_label(left, "ALGORITHM", pady=(16,4))
        algo_card = tk.Frame(left, bg=CARD)
        algo_card.pack(fill="x")
        af = tk.Frame(algo_card, bg=CARD)
        af.pack(fill="x", padx=10, pady=10)

        self.algo_var = tk.StringVar(value="FCFS")
        algos = ["FCFS","SJF","SRT","Round Robin","Priority (NP)","Priority + RR","Run All"]
        self.algo_combo = ttk.Combobox(af, textvariable=self.algo_var,
                                       values=algos, state="readonly",
                                       font=("Segoe UI", 10), width=22)
        self.algo_combo.pack(fill="x")
        self.algo_combo.bind("<<ComboboxSelected>>", self._on_algo_change)

        # Quantum row (shown for RR-based)
        self.quantum_frame = tk.Frame(algo_card, bg=CARD)
        tk.Label(self.quantum_frame, text="Time Quantum", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        self.quantum_var = tk.IntVar(value=2)
        ttk.Spinbox(self.quantum_frame, from_=1, to=99,
                    textvariable=self.quantum_var, width=5,
                    font=("Segoe UI", 10)).pack(side="left", padx=(8,0))

        # Priority direction row
        self.pri_dir_frame = tk.Frame(algo_card, bg=CARD)
        tk.Label(self.pri_dir_frame, text="Priority Direction", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        self.pri_dir_var = tk.StringVar(value="Lower = Higher")
        ttk.Combobox(self.pri_dir_frame, textvariable=self.pri_dir_var,
                     values=["Lower = Higher Priority","Higher = Higher Priority"],
                     state="readonly", width=22,
                     font=("Segoe UI", 9)).pack(side="left", padx=(8,0))

        self._on_algo_change()  # set initial visibility
    
        # ── Stats cards ──
        self._section_label(left, "SUMMARY TABLE", pady=(16,4))
        stats = tk.Frame(left, bg=BG)
        stats.pack(fill="x")
        
        stats.columnconfigure(0, weight=1)
        stats.columnconfigure(1, weight=1)

        self.avg_tat_card = self._stat_card(stats, "Avg TAT", "—", "Turnaround Time")
        self.avg_tat_card.grid(row=0, column=0, sticky="ew", padx=(0,6))
        self.avg_wt_card  = self._stat_card(stats, "Avg WT",  "—", "Waiting Time")
        self.avg_wt_card.grid(row=0, column=1, sticky="ew")
        
        self.processCount = self._stat_card(stats, "Processes", "—", "Total Process")
        self.processCount.grid(row=1, column=0, sticky="ew", padx=(0,6), pady=(6,0))
        
        self.algoUsed = self._stat_card(stats, "Algorithm", "—", "Used Method")
        self.algoUsed.grid(row=1, column=1, sticky="ew", pady=(6,0))

    # right side
    def _build_right(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        # ── Gantt Section ──
        tk.Label(right, text="GANTT CHART", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", pady=(0, 4))

        gantt_card = tk.Frame(right, bg=CARD)
        gantt_card.pack(fill="x", pady=(0, 12))

        self.gantt_canvas = tk.Canvas(gantt_card, bg=CARD,
                                      highlightthickness=0, height=170)
        self.gantt_canvas.pack(fill="x", padx=8, pady=(8, 0))

        gsc = ttk.Scrollbar(gantt_card, orient="horizontal",
                            command=self.gantt_canvas.xview)
        gsc.pack(fill="x", padx=8, pady=(0, 8))
        self.gantt_canvas.configure(xscrollcommand=gsc.set)

        # ── Table Section ──
        tk.Label(right, text="RESULTS TABLE", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", pady=(0, 4))

        table_card = tk.Frame(right, bg=CARD)
        table_card.pack(fill="both", expand=True)

        # Inner frame for treeview + scrollbar side by side
        tree_frame = tk.Frame(table_card, bg=CARD)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

        cols = ("pid", "at", "bt", "priority", "finish", "tat", "wt")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                  show="headings", selectmode="none")
        heads = [("pid","PID",60),("at","Arrival",70),("bt","Burst",60),
                 ("priority","Priority",70),("finish","Finish",70),
                 ("tat","TAT",70),("wt","WT",70)]
        for col, label, width in heads:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center", minwidth=50)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("alt", background="#1e2235")

        self._draw_placeholder()

    # ── Helper widgets ───────────────────────────
    def _section_label(self, parent, text, pady=(0,4), side=None):
        lbl = tk.Label(parent, text=text,
                       bg=BG, fg=MUTED, font=("Segoe UI", 8, "bold"))
        lbl.pack(fill="x", pady=pady, anchor="w")
        return lbl

    #button template
    def _flat_btn(self, parent, text, cmd, fg=TEXT, bg=CARD):
        return tk.Button(parent, text=text, fg=fg,
                         font=("Segoe UI", 9), relief="flat",
                         cursor="hand2", activebackground=BORDER,
                         activeforeground=fg, command=cmd, bg=CARD,
                         padx=8, pady=4)
        

    def _stat_card(self, parent, title, value, subtitle):
        f = tk.Frame(parent, bg=CARD, pady=8)
        tk.Label(f, text=title, bg=CARD, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack()
        val_lbl = tk.Label(f, text=value, bg=CARD, fg=ACCENT2,
                           font=("Segoe UI", 20, "bold"))
        val_lbl.pack()
        tk.Label(f, text=subtitle, bg=CARD, fg=MUTED,
                 font=("Segoe UI", 8)).pack()
        f._val_lbl = val_lbl
        return f

    def _update_stat(self, card, value):
        card._val_lbl.config(text=value)

    # ── Process rows ─────────────────────────────
    def _add_process_row(self):
        idx = len(self.proc_rows)
        pid = f"P{idx+1}"
        row = tk.Frame(self.proc_frame, bg=CARD)
        row.pack(fill="x", pady=5)
 
        # Color swatch
        color = PROC_COLORS[idx % len(PROC_COLORS)]
        tk.Label(row, text="█", bg=CARD, fg=color,
                 font=("Segoe UI", 12), width=2).pack(side="left")
 
        at_v  = tk.StringVar(value="0") #inital values
        bt_v  = tk.StringVar(value="1")
        pri_v = tk.StringVar(value="1")
 
        pid_lbl = tk.Label(row, text=pid, bg=CARD, fg=TEXT,
                           font=("Consolas", 10, "bold"), width=4)
        pid_lbl.pack(side="left")

        #entries table for process ui
        entries = []
        for var, w in [(at_v,5),(bt_v,5),(pri_v,5)]:
            e = tk.Entry(row, textvariable=var, width=w+2,
                         bg=PANEL, fg=TEXT, insertbackground=TEXT,
                         relief="flat", font=("Consolas", 10),
                         highlightthickness=1,
                         highlightbackground=BORDER,
                         highlightcolor=ACCENT)
            e.pack(side="left", padx=13)
            entries.append(e)
 
        def _mw(e, canvas=self._proc_canvas):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        for widget in [row, pid_lbl] + entries:
            widget.bind("<MouseWheel>", _mw)
 
        self.proc_rows.append((pid, at_v, bt_v, pri_v, row))
        
            
        tk.Button(
            row,
            text="─",
            fg=ERROR,
            bg=CARD,
            bd=0,
            padx=20,
            cursor="hand2",
            command=lambda r=row, item=(pid, at_v, bt_v, pri_v, row): 
                self._remove_process(r, item)
        ).pack(side="right", padx=5)
    
    
    def _remove_process(self, r, item):
        if len(self.proc_rows) <= 3:
            messagebox.showwarning("Minimum", "At least 3 processes required.")
            return

        r.destroy()
        self.proc_rows.remove(item)

    # remove process
    # def _remove_last_row(self):
    #     if len(self.proc_rows) <= 3:
    #         messagebox.showwarning("Minimum", "At least 3 processes required.")
    #         return
    #     _, _, _, _, row = self.proc_rows.pop()
    #     row.destroy()
    
    #reset all process
    def _reset_processes(self):
        # destroy all existing rows
        for _, _, _, _, row in self.proc_rows:
            row.destroy()

        # clear the list
        self.proc_rows.clear()

        # recreate initial 3 processes (default values)
        for i in range(3):
            self._add_process_row()
    
    # clear process
    def _clear_all_process(self):
        print("ROWS:", self.proc_rows)
        
        for _, pid_v, at_v, bt_v, _ in self.proc_rows:
            pid_v.set(0)
            at_v.set(1)
            bt_v.set(1)
            
        # self.proc_rows.clear()
        

    # ── Algorithm options visibility ─────────────
    def _on_algo_change(self, _=None):
        algo = self.algo_var.get()
        needs_quantum   = algo in ("Round Robin", "Priority + RR", "Run All")
        needs_pri_dir   = algo in ("Priority (NP)", "Priority + RR", "Run All")

        if needs_quantum:
            self.quantum_frame.pack(fill="x", padx=10, pady=(4,0))
        else:
            self.quantum_frame.pack_forget()

        if needs_pri_dir:
            self.pri_dir_frame.pack(fill="x", padx=10, pady=(4,8))
        else:
            self.pri_dir_frame.pack_forget()
            self.quantum_frame.pack_configure(pady=(4,8)) if needs_quantum else None

    # ── Run ──────────────────────────────────────
    def _run_simulation(self):
        # Parse processes
        processes = []
        for i, (pid, at_v, bt_v, pri_v, _) in enumerate(self.proc_rows):
            try:
                at  = int(at_v.get())
                bt  = int(bt_v.get())
                pri = int(pri_v.get())
                if bt <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Input Error",
                    f"{pid}: All fields must be integers, Burst Time > 0.")
                return
            processes.append({"pid": pid, "at": at, "bt": bt,
                               "priority": pri, "remaining": bt,
                               "finish": 0, "start": -1})

        algo    = self.algo_var.get()
        quantum = self.quantum_var.get()
        hib     = self.pri_dir_var.get() == "Higher = Higher Priority"

        # Assign colors
        self.color_map = {p["pid"]: PROC_COLORS[i % len(PROC_COLORS)]
                          for i, p in enumerate(processes)}

        # Run selected algorithm(s)
        if algo == "FCFS":
            gantt, results = run_fcfs(processes)
            self._display(gantt, results, "First-Come, First-Served")

        elif algo == "SJF":
            gantt, results = run_sjf(processes)
            self._display(gantt, results, "Shortest Job First (NP)")

        elif algo == "SRT":
            gantt, results = run_srt(processes)
            self._display(gantt, results, "Shortest Remaining Time")

        elif algo == "Round Robin":
            gantt, results = run_rr(processes, quantum)
            self._display(gantt, results, f"Round Robin (q={quantum})")

        elif algo == "Priority (NP)":
            gantt, results = run_priority_np(processes, hib)
            mode = "High>Hi" if hib else "Low>Hi"
            self._display(gantt, results, f"Priority NP ({mode})")

        elif algo == "Priority + RR":
            gantt, results = run_priority_rr(processes, quantum, hib)
            mode = "High>Hi" if hib else "Low>Hi"
            self._display(gantt, results, f"Priority+RR q={quantum} ({mode})")

        elif algo == "Run All":
            # Run all and show combined in a new window
            self._run_all(processes, quantum, hib)

    def _display(self, gantt, results, title):
        self._draw_gantt(gantt)
        self._fill_table(results)
        n     = len(results)
        avg_tat = sum(r["tat"] for r in results) / n
        avg_wt  = sum(r["wt"]  for r in results) / n
        self._update_stat(self.avg_tat_card, f"{avg_tat:.2f}")
        self._update_stat(self.avg_wt_card,  f"{avg_wt:.2f}")
        self._update_stat(self.algoUsed, f"{self.algo_var.get()}")
        self._update_stat(self.processCount, f"{n}")

    # ── Gantt Chart ──────────────────────────────
    def _draw_placeholder(self):
        c = self.gantt_canvas
        c.delete("all")
        c.create_text(400, 80,
                      text="-",
                      fill=MUTED, font=("Segoe UI", 11), anchor="center")

    def _draw_gantt(self, gantt):
        c = self.gantt_canvas
        c.delete("all")
        if not gantt:
            return

        BLOCK_H  = 44
        LABEL_H  = 24
        TIMELINE = 18
        TOP      = 20
        PX_PER_T = 38  # pixels per time unit

        total_end = gantt[-1]["end"]
        canvas_w  = max(total_end * PX_PER_T + 80, 600)
        c.configure(scrollregion=(0, 0, canvas_w, BLOCK_H + LABEL_H + TIMELINE + TOP + 30))

        # Timeline ticks
        for t in range(total_end + 1):
            x = 40 + t * PX_PER_T
            c.create_line(x, TOP + BLOCK_H, x, TOP + BLOCK_H + 6,
                          fill=MUTED, width=1)
            c.create_text(x, TOP + BLOCK_H + TIMELINE,
                          text=str(t), fill=MUTED,
                          font=("Consolas", 8), anchor="center")

        # Blocks
        for seg in gantt:
            x1 = 40 + seg["start"] * PX_PER_T
            x2 = 40 + seg["end"]   * PX_PER_T
            y1 = TOP
            y2 = TOP + BLOCK_H
            pid   = seg["pid"]
            color = self.color_map.get(pid, ACCENT)

            # Block
            c.create_rectangle(x1, y1, x2, y2,
                                fill=color, outline=BG, width=2)
            # Label
            bw = x2 - x1
            if bw > 20:
                c.create_text((x1+x2)//2, (y1+y2)//2,
                              text=pid, fill="white",
                              font=("Segoe UI", 9, "bold"), anchor="center")

        # CPU bar label
        c.create_text(32, TOP + BLOCK_H//2,
                      text="CPU", fill=MUTED,
                      font=("Segoe UI", 8, "bold"), anchor="e")

    # ── Results Table ────────────────────────────
    def _fill_table(self, results):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, r in enumerate(results):
            tag = ("alt",) if i % 2 else ()
            self.tree.insert("", "end", values=(
                r["pid"], r["at"], r["bt"], r["priority"],
                r["finish"], r["tat"], r["wt"]
            ), tags=tag)
            # Color the PID cell using a tag
            pid_tag = f"pid_{r['pid']}"
            color = self.color_map.get(r["pid"], ACCENT)
            self.tree.tag_configure(pid_tag, foreground=color)

    # ── Run All window ───────────────────────────
    def _run_all(self, processes, quantum, hib):
        win = tk.Toplevel(self)
        win.title("All Algorithms — Comparison")
        win.configure(bg=BG)
        win.geometry("1100x750")

        tk.Label(win, text="All Algorithms Comparison",
                 bg=BG, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(pady=(16,4))
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=24)

        # Scrollable canvas
        outer = tk.Frame(win, bg=BG)
        outer.pack(fill="both", expand=True, padx=16, pady=8)
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        vscroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        vscroll.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=vscroll.set)

        content = tk.Frame(canvas, bg=BG)
        cwin = canvas.create_window((0,0), window=content, anchor="nw")
        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(cwin, width=e.width)
        content.bind("<Configure>", _resize)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cwin, width=e.width))

        mode = "High>Hi" if hib else "Low>Hi"
        algos = [
            ("FCFS",                       run_fcfs(processes)),
            ("SJF (Non-Preemptive)",        run_sjf(processes)),
            ("SRT (Preemptive)",            run_srt(processes)),
            (f"Round Robin (q={quantum})",  run_rr(processes, quantum)),
            (f"Priority NP ({mode})",       run_priority_np(processes, hib)),
            (f"Priority+RR q={quantum} ({mode})", run_priority_rr(processes, quantum, hib)),
        ]

        for name, (gantt, results) in algos:
            n       = len(results)
            avg_tat = sum(r["tat"] for r in results) / n
            avg_wt  = sum(r["wt"]  for r in results) / n

            sec = tk.Frame(content, bg=CARD)
            sec.pack(fill="x", pady=6, padx=4)

            # Header
            hf = tk.Frame(sec, bg=BORDER)
            hf.pack(fill="x")
            tk.Label(hf, text=f"  {name}", bg=BORDER, fg=TEXT,
                     font=("Segoe UI", 11, "bold"), pady=6).pack(side="left")
            tk.Label(hf, text=f"Avg TAT: {avg_tat:.2f}  |  Avg WT: {avg_wt:.2f}  ",
                     bg=BORDER, fg=ACCENT2,
                     font=("Segoe UI", 10)).pack(side="right")

            # Mini Gantt
            mini = tk.Canvas(sec, bg=CARD, height=80, highlightthickness=0)
            mini.pack(fill="x", padx=8, pady=6)
            self._draw_mini_gantt(mini, gantt)

            # Mini table
            cols = ("pid","at","bt","finish","tat","wt")
            tr = ttk.Treeview(sec, columns=cols, show="headings",
                              height=len(results), selectmode="none")
            for col, lbl, w in [("pid","PID",50),("at","AT",60),("bt","BT",55),
                                  ("finish","Finish",65),("tat","TAT",60),("wt","WT",60)]:
                tr.heading(col, text=lbl); tr.column(col, width=w, anchor="center")
            for i, r in enumerate(results):
                tag = ("alt",) if i%2 else ()
                tr.insert("", "end", values=(r["pid"],r["at"],r["bt"],
                                              r["finish"],r["tat"],r["wt"]), tags=tag)
            tr.tag_configure("alt", background="#1e2235")
            tr.pack(fill="x", padx=8, pady=(0,8))

    def _draw_mini_gantt(self, canvas, gantt):
        """Compact Gantt for the Run All window."""
        canvas.update_idletasks()
        W = canvas.winfo_width() or 900
        total = gantt[-1]["end"] if gantt else 1
        scale = (W - 60) / total
        BH, TOP = 28, 14

        for seg in gantt:
            x1 = 40 + seg["start"] * scale
            x2 = 40 + seg["end"]   * scale
            pid   = seg["pid"]
            color = self.color_map.get(pid, ACCENT)
            canvas.create_rectangle(x1, TOP, x2, TOP+BH,
                                    fill=color, outline=BG, width=1)
            if (x2-x1) > 16:
                canvas.create_text((x1+x2)/2, TOP+BH/2,
                                   text=pid, fill="white",
                                   font=("Segoe UI", 8, "bold"))
        # ticks
        for seg in gantt:
            for t in [seg["start"], seg["end"]]:
                x = 40 + t * scale
                canvas.create_line(x, TOP+BH, x, TOP+BH+6, fill=MUTED)
                canvas.create_text(x, TOP+BH+13, text=str(t),
                                   fill=MUTED, font=("Consolas", 7))


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = CPUSchedulerApp()
    app.mainloop()
