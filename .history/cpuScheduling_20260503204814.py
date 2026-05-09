#final
import copy
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

#MAIN APP ENTRY POINT
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()



# UTILS
# bg color palette
BG        = "#1B211A"  
PANEL     = "#232C22"  
CARD      = "#2C3A2B"  
BORDER    = "#3E4A3A"  
ACCENT    = "#628141" 
ACCENT2   = "#8BAE66"  
TEXT      = "#EBD5AB" 
MUTED     = "#A8B39A"  
ERROR     = "#C96A5B"  
WARNING   = "#C2A25A"  
SUCCESS   = "#7FAE7A"  
PINK      = "#F4A7B9"  

# list of colors for process identifier
processColors = [
    "#8b93a7",  
    "#7fbf9b",  
    "#d46a6a",  
    "#c9a66b",  
    "#a7b3c6",  
    "#89a7c7",  
    "#c58c7a",  
    "#b46b7a",  
    "#7a8fb5",  
    "#b39ddb",  
    "#9ccc65",  
    "#64b5f6",  
    "#f48fb1", 
    "#ce93d8",  
    "#80cbc4",  
]
# END OF UTILS


#GENERAL FUNCTION
def reset(processes): # resets process
    procs = copy.deepcopy(processes)
    for p in procs:
        p["remaining"] = p["bt"]
        p["finish"] = 0
        p["start"] = -1
    return procs

def computeTaT_WT(processes): #function for solving Turn Around and Waiting Time
    results = []
    for p in processes:
        tat = p["finish"] - p["at"]
        wt  = tat - p["bt"]
        results.append({**p, "tat": tat, "wt": wt})
    return results

#END OF GENERAL FUNCTION



# SOLVING FUNCTIONS / LOGIC FOR EACH ALGORITHM

#function for solving FCFS Algorithm 
def solveFCFS(processes):
    procs = sorted(reset(processes), key=lambda p: (p["at"], int(p["pid"][1:]))) #sorts the process based on their arrival time, if equal at it will sort by process id
    time, gantt = 0, []
    for p in procs:    # loop through the procs array (sorted version)
        if time < p["at"]: time = p["at"]  
        p["start"] = time
        time += p["bt"]            #FCFS ALGORITHM
        p["finish"] = time
        gantt.append({"pid": p["pid"], "start": time - p["bt"], "end": time}) #add to gant table with values: pid, start and end time
    return gantt, computeTaT_WT(procs)  # calls computeTaT_WT to calculate TAT and WT

#function for solving SJF Algorithm
def solveSJF(processes):
    procs, done, gantt, time = reset(processes), [], [], 0 # resets  data, initialize lists and time
    remaining = procs[:]
    while remaining:   # loop until all process are done
        avail = [p for p in remaining if p["at"] <= time]  #check if there are process that have arrived
        if not avail:       # if none, it will go to the next at
            time = min(p["at"] for p in remaining); continue
        p = min(avail, key=lambda x: (x["bt"], x["at"], x["pid"])) # this function picks the shortest burts time
        remaining.remove(p)
        p["start"] = time
        gantt.append({"pid": p["pid"], "start": time, "end": time + p["bt"]}) # add to the gannt chart list
        time += p["bt"]; p["finish"] = time; done.append(p)
    return gantt, computeTaT_WT(done) # compute TAT and WT

#function for solving SRT
def solveSRT(processes):
    procs = reset(processes) #reset data
    n, time, done, gantt = len(procs), 0, 0, [] #initialize lists and time
    while done < n: #loop until all process are done
        avail = [p for p in procs if p["at"] <= time and p["remaining"] > 0]  # gets process that have arrived and still have remaining time (nnumber of burst time)
        if not avail: time += 1; continue  #if none, it will be idle and will add +1 to the time to
        p = min(avail, key=lambda x: (x["remaining"], x["at"], x["pid"])) # selects process with shortest remaining time
        if p["start"] == -1: p["start"] = time
        if gantt and gantt[-1]["pid"] == p["pid"]:  #update gantt chart
            gantt[-1]["end"] = time + 1
        else:
            gantt.append({"pid": p["pid"], "start": time, "end": time + 1})
        p["remaining"] -= 1; time += 1
        if p["remaining"] == 0:
            p["finish"] = time; done += 1
    return gantt, computeTaT_WT(procs) # compute TAT and WT

#function for solving RR with Quantum
def solveRoundRobin(processes, quantum):
    procs   = reset(processes) #reset process
    procs_s = sorted(procs, key=lambda p: p["at"]) #sort process by arrival time
    
    #initialize values
    queue, gantt, time, arrived = [], [], 0, set() 
    idx, n, done = 0, len(procs_s), 0
    
    #adds all the process that arrive each time (this is for ready queue)
    while idx < n and procs_s[idx]["at"] <= time:           
        queue.append(procs_s[idx]); arrived.add(procs_s[idx]["pid"]); idx += 1
    
    
    while done < n: #loop until all process are finished
        
        if not queue: #if no process are ready at the moment, it will increment to the next arrival time
            time = procs_s[idx]["at"]
            while idx < n and procs_s[idx]["at"] <= time:
                queue.append(procs_s[idx]); arrived.add(procs_s[idx]["pid"]); idx += 1
                
        p = queue.pop(0) # take first process in queue
        
        if p["start"] == -1: 
            p["start"] = time
        
        run = min(quantum, p["remaining"]) # run for quantum or remaining time if it is smaller than quantum
        
        gantt.append({"pid": p["pid"], "start": time, "end": time + run}) #add process to gantt list
        
        time += run; 
        p["remaining"] -= run
        
        # add newly arrived processes during execution
        while idx < n and procs_s[idx]["at"] <= time:
            queue.append(procs_s[idx]); arrived.add(procs_s[idx]["pid"]); idx += 1
            
        if p["remaining"] > 0:
            queue.append(p) #if process is still not finished, it will append to list again
        else: 
            p["finish"] = time; 
            done += 1 #mark as finished
            
    return gantt, computeTaT_WT(procs) # compute TAT, WT and RETURN gantt list

# function for solving Priority Preemptive
def run_priority_p(processes, higher_is_better):
    procs = reset(processes) #reset process
    
    n, time, done, gantt = len(procs), 0, 0, [] #initialize
    
    sign = -1 if higher_is_better else 1 #check for priority meaning: -1 means higher number(priority), 1 means lower number(priority)
    
    while done < n:  #run until all process are done
        
        avail = [p for p in procs if p["at"] <= time and p["remaining"] > 0] #get all process that have arrived and are not yet finished
        
        if not avail:
            time += 1; # if idle, move to necxt arrival time
            continue
        
        # pick process with best priority, if tie, it will choose between arrival time then pid
        p = min(avail, key=lambda x: (sign * x["priority"], x["at"], x["pid"]))
        
        if p["start"] == -1: # for first time the process have arrived
            p["start"] = time
            
        
        if gantt and gantt[-1]["pid"] == p["pid"]: # append to gantt list
            gantt[-1]["end"] = time + 1
        else:
            gantt.append({"pid": p["pid"], "start": time, "end": time + 1})
            
        p["remaining"] -= 1; time += 1
        
        if p["remaining"] == 0: #if finished, 
            p["finish"] = time #completion time
            done += 1 
            
    return gantt, computeTaT_WT(procs) #return gantt list and call function compute TAT and WT

# function for solving Priority Non Preemptive
def run_priority_np(processes, higher_is_better):
    procs = reset(processes) #reset process
    
    done, gantt, time = [], [], 0 #initialize 
    
    remaining = procs[:] # # copy of processes not yet executed

    sign = -1 if higher_is_better else 1 #check for priority meaning: -1 means higher number(priority), 1 means lower number(priority)
    
    
    while remaining: #run until all process are not yet done
        
        avail = [p for p in remaining if p["at"] <= time] #get all process that have arrived and are not yet finished
        
        if not avail: 
            time = min(p["at"] for p in remaining);  # if idle, move to necxt arrival time
            continue
        
        p = min(avail, key=lambda x: (sign * x["priority"], x["at"], x["pid"]))  # pick process with best priority, if tie, it will choose between arrival time then pid
        
        remaining.remove(p) # remove current process from queue
        
        p["start"] = time # record start time
        
        gantt.append({"pid": p["pid"], "start": time, "end": time + p["bt"]}) # add to gantt list
        
        time += p["bt"] # run process to completion
        
        p["finish"] = time # record finish time
        
        done.append(p) #adds done process to done list
        
    return gantt, computeTaT_WT(done)#return gantt list and call function compute TAT and WT


#function for solving Priority with Round Robin
def run_priority_rr(processes, quantum, higher_is_better):
    
    procs  = reset(processes)  #resets process
    
    #initialize
    queue, gantt, time = [], [], 0
    
    sign   = -1 if higher_is_better else 1 #check for priority meaning: -1 means higher number(priority), 1 means lower number(priority)
    
    procs_s = sorted(procs, key=lambda p: (p["at"], sign * p["priority"])) # sort by arrival time if equal, will check priority
    
    idx, n, done = 0, len(procs_s), 0
    
     # function to add newly arrived processes into queue
    def enqueue():
        nonlocal idx
        
        while idx < n and procs_s[idx]["at"] <= time:
            queue.append(procs_s[idx]) # add process to ready queue
            idx += 1 
        queue.sort(key=lambda x: (sign * x["priority"], x["at"])) # pick process with best priority
    
    enqueue()
    
    while done < n: # run until all processes are finished
        
        if not queue: #if no process arrived, move to next arrival time
            time = procs_s[idx]["at"]
            enqueue()
            
        p = queue.pop(0) # pick highest priority process in queue
        
        if p["start"] == -1:
            p["start"] = time # first time process runs
            
        run = min(quantum, p["remaining"]) # run for quantum or remaining time if it is smaller than quantum
        
        gantt.append({"pid": p["pid"], "start": time, "end": time + run}) # add to gantt list
        
        time += run # increment time
        
        p["remaining"] -= run #reduce remaining time
        
        enqueue()  # check for new arrivals during execution

        if p["remaining"] > 0:
            queue.append(p) #append back to queue if not yet finished
            queue.sort(key=lambda x: (sign * x["priority"], x["at"])) #resort by priority after re adding
        else: 
            p["finish"] = time # mark completion time
            done += 1
            
    return gantt, computeTaT_WT(procs) #return gantt list and call function compute TAT and WT

# END OF SOLVING FUNCTIONS / LOGIC FOR EACH ALGORITHM



# utility functions
# class Tooltip:
#     def __init__(self, widget, text):
#         self.widget = widget
#         self.text   = text
#         self.tip    = None
#         widget.bind("<Enter>", self.show)
#         widget.bind("<Leave>", self.hide)

#     def show(self, _=None):
#         x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget,"bbox") else (0,0,0,0)
#         x += self.widget.winfo_rootx() + 20
#         y += self.widget.winfo_rooty() + 20
#         self.tip = tw = tk.Toplevel(self.widget)
#         tw.wm_overrideredirect(True)
#         tw.wm_geometry(f"+{x}+{y}")
#         lbl = tk.Label(tw, text=self.text, background="#2e3250", foreground=TEXT,
#                        relief="flat", padx=8, pady=4,
#                        font=("Consolas", 9))
#         lbl.pack()

#     def hide(self, _=None):
#         if self.tip: self.tip.destroy(); self.tip = None
     
# end of utility functions

# MAIN APPLICATION
class MainApp(tk.Tk):
    
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

        self.setUpGeneralStyles() # set up general styles
        self.buildUI() # build ui
        
    # general styles
    def setUpGeneralStyles(self):
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

    # MAIN UI
    def buildUI(self):
       # HEADER CONTAINER
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(16, 0))
 
        # LEFT SIDE OF HEADER (TITLE)
        leftSideHeader = tk.Frame(header, bg=BG)
        leftSideHeader.pack(side="left")
        tk.Label(leftSideHeader, text="⚙  CPU Scheduling Simulator",
                 bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(leftSideHeader, text="OS Process Management",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(10, 0), pady=(5, 0))
 
        # RIGHT SIDE OF HEADER (RESET AND RUN BUTTON)
        rightSideHeader = tk.Frame(header, bg=BG)
        rightSideHeader.pack(side="right")
        
        # Reset button
        self.buttonTemplate(rightSideHeader, "↺ RESET", self.resetProcess,
                    fg="white", font=("Segoe UI", 10, "bold"), bg=ERROR).pack(side="left", padx=(8, 0))
        
        # Run button
        tk.Button(rightSideHeader, text="▶  Run", bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  activebackground="#5a52d5", activeforeground="white", padx=14, pady=6, command=self.runApp).pack(side="left", padx=(8, 0))
        
        # END OF HEADER CONTAINER
        
        # MAIN PANEL
        mainPanel = tk.Frame(self, bg=BG)
        mainPanel.pack(fill="both", expand=True, padx=24, pady=16)
        mainPanel.columnconfigure(0, weight=0, minsize=320)
        mainPanel.columnconfigure(1, weight=1)
        mainPanel.rowconfigure(0, weight=1)

        self.buildLeftPanel(mainPanel)
        self.buildRightPanel(mainPanel)

    # LEFT SIDE OF MAIN PANEL
    def buildLeftPanel(self, parent):
        left = tk.Frame(parent, bg=BG)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 16))

        #  OUTER CONTAINER FOR USER INPUT (Algorithm AND Processes) 
        outerContainer = tk.Frame(left, bg=CARD, bd=0)
        outerContainer.pack(fill="x")

        # USER INPUT TITLE
        tk.Label(outerContainer, text="USER INPUT", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", pady=(0, 4))

        # ALGORITHM TITLE
        tk.Label(outerContainer, text="ALGORITHM", bg=CARD, fg=TEXT, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        
        #ALGORITHM CONTAINER
        algoContainer = tk.Frame(outerContainer, bg=CARD)
        algoContainer.pack(fill="x", padx=10, pady=(0, 8))
        
        af = tk.Frame(algoContainer, bg=CARD)
        af.pack(fill="x", padx=10, pady=10)

        self.algoSelected = tk.StringVar(value="FCFS")
        listOfAlgo = ["FCFS","SJF","SRT","Round Robin","Priority (NP)","Priority (P)","Priority + RR","Run All"]
        self.algoComboBox = ttk.Combobox(af, textvariable=self.algoSelected,
                                       values=listOfAlgo, state="readonly",
                                       font=("Segoe UI", 10), width=22)
        self.algoComboBox.pack(fill="x")
        self.algoComboBox.bind("<<ComboboxSelected>>", self.changeAlgo)

        # Quantum Section (visible in RR-based Algorithm)
        self.quantumContainer = tk.Frame(algoContainer, bg=CARD)
        tk.Label(self.quantumContainer, text="Time Quantum", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 9)).pack(side="left")
        self.quantumValue = tk.IntVar(value=2)
        ttk.Spinbox(self.quantumContainer, from_=1, to=99,
                    textvariable=self.quantumValue, width=5,
                    font=("Segoe UI", 10)).pack(side="left", padx=(8,0))

        # Priority Section
        self.priorityContainer = tk.Frame(algoContainer, bg=CARD)
        tk.Label(self.priorityContainer, text="Priority Value", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 9)).pack(side="left")
        self.priorityValue = tk.StringVar(value="Lower = Higher")
        ttk.Combobox(self.priorityContainer, textvariable=self.priorityValue,
                     values=["Lower = Higher Priority","Higher = Higher Priority"],
                     state="readonly", width=22,
                     font=("Segoe UI", 9)).pack(side="left", padx=(8,0))

        self.changeAlgo()  # set initial visibility

        
        # Initial Number of Process Input
        numberProcessContainer = tk.Frame(outerContainer, bg=CARD)
        numberProcessContainer.pack(fill="x", padx=10, pady=10)

        tk.Label(numberProcessContainer, text="Number of Processes:",
                 bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left")

        self.numberProcessValue = tk.IntVar(value=3)
        ttk.Spinbox(numberProcessContainer,
                    textvariable=self.numberProcessValue, width=40,
                    font=("Segoe UI", 10)).pack(side="left", padx=(8, 6))

        # Generate Process Button
        tk.Button(numberProcessContainer, text="Generate",
                  bg=ACCENT, fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2",
                  activebackground="#4e6832",
                  activeforeground="white",
                  padx=8, pady=2,
                  command=self.generateProcessFunctioj).pack(side="right")
        
        # Process Label and Generate Section
        ProcessAndButtonLabel = tk.Frame(outerContainer, bg=CARD)
        ProcessAndButtonLabel.pack(fill="x", padx=10, pady=(8, 2))

        tk.Label(ProcessAndButtonLabel, text="PROCESSES",
                 bg=CARD, fg=TEXT,
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        btn_row = tk.Frame(ProcessAndButtonLabel, bg=CARD)
        btn_row.pack(side="right")

        self.buttonTemplate(btn_row, "ADD PROCESS", self.addProcessFunction, #Add Process Button
                    fg="white", bg=ACCENT).pack(side="left")
        
        self.buttonTemplate(btn_row, "CLEAR VALUES", self.clearValuesFunction, #Clear Values Button
                    fg=ACCENT, bg=TEXT).pack(side="left", padx=(8, 0))
        
        
        # PROCESS CONTAINER
        inputProcessContainer = tk.Frame(outerContainer, bg=BG, bd=0)
        inputProcessContainer.pack(fill="x", padx=10, pady=10)

        # COLUMN HEADER TITLE FOR PROCESS (PID, AT, BT, PRIO)
        hdr = tk.Frame(inputProcessContainer, bg=BG)
        hdr.pack(fill="x", padx=70, pady=10)
        for col, w, txt in [("PID",7,"PID"),("Arrival Time",10,"Arrival Time"),("Burst Time",10,"Burst Time"),("Priority",10,"Priority"),("",3,"")]:
            tk.Label(hdr, text=txt, bg=BG, fg=TEXT,
                     font=("Segoe UI", 8, "bold"), width=w, anchor="center").pack(side="left")

        # Scrollable Section IN PROCESS CONTAINER
        scrollableSection = tk.Frame(inputProcessContainer, bg=BG)
        scrollableSection.pack(fill="x", padx=10, pady=(0, 10))

        self._proc_canvas = tk.Canvas(scrollableSection, bg=BG,
                                      highlightthickness=0, height=120)
        self._proc_canvas.pack(side="left", fill="x", expand=True, padx=(50, 0))

        proc_vsb = ttk.Scrollbar(scrollableSection, orient="vertical",
                                  command=self._proc_canvas.yview)
        proc_vsb.pack(side="right", fill="y")
        self._proc_canvas.configure(yscrollcommand=proc_vsb.set)

        self.proc_frame = tk.Frame(self._proc_canvas, bg=BG)
        self._proc_canvas_window = self._proc_canvas.create_window(
            (0, 0), window=self.proc_frame, anchor="nw"
        )

        def _on_proc_frame_configure(e):
            self._proc_canvas.configure(scrollregion=self._proc_canvas.bbox("all"))
            row_h = self.proc_frame.winfo_reqheight()
            self._proc_canvas.configure(height=min(row_h, 310))

        def _on_proc_canvas_configure(e):
            self._proc_canvas.itemconfig(self._proc_canvas_window, width=e.width)

        def _on_mousewheel(e):
            self._proc_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        # BINDERS / CONNECTS THEM ALL
        self.proc_frame.bind("<Configure>", _on_proc_frame_configure)
        self._proc_canvas.bind("<Configure>", _on_proc_canvas_configure)
        self._proc_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.proc_frame.bind("<MouseWheel>", _on_mousewheel)

        # ADD 3 PROCESS AS INITIAL INPUT
        self.addProcessFunction()
        self.addProcessFunction()
        self.addProcessFunction()
    
        # SUMMARY TABLE SECTION
        self.sectionLabel(left, "SUMMARY TABLE", pady=(16,4))
        stats = tk.Frame(left, bg=BG)
        stats.pack(fill="x")
        
        stats.columnconfigure(0, weight=1)
        stats.columnconfigure(1, weight=1)

        #Container for Average TAT in SUMMARY SECTION
        self.averageTATContainer = self._stat_card(stats, "Avg TAT", "—", "Turnaround Time")
        self.averageTATContainer.grid(row=0, column=0, sticky="ew", padx=(0,6))
        
        #Container for Average WT in SUMMARY SECTION
        self.averageWTContainer  = self._stat_card(stats, "Avg WT",  "—", "Waiting Time")
        self.averageWTContainer.grid(row=0, column=1, sticky="ew")
        
        #Container for Process Count in SUMMARY SECTION
        self.processCount = self._stat_card(stats, "Processes", "—", "Total Process")
        self.processCount.grid(row=1, column=0, sticky="ew", padx=(0,6), pady=(6,0))
        
         #Container for Algorithm Used in SUMMARY SECTION
        self.algoUsed = self._stat_card(stats, "Algorithm", "—", "Used Method")
        self.algoUsed.grid(row=1, column=1, sticky="ew", pady=(6,0))

        #END OF SUMMARY TABLE SECTION
        
        
    # RIGHT SIDE OF MAIN PANEL
    def buildRightPanel(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        # GANTT SECTION
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

        # TABLE SECTION
        tk.Label(right, text="RESULTS TABLE", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", pady=(0, 4))

        table_card = tk.Frame(right, bg=CARD)
        table_card.pack(fill="both", expand=True)

        # Inner frame for SCROLLBAR
        tree_frame = tk.Frame(table_card, bg=CARD)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

        #Label for Results Table
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

        self.initializeGantt()

    # ── Helper widgets ───────────────────────────
    def sectionLabel(self, parent, text, pady=(0,4), side=None):
        lbl = tk.Label(parent, text=text,
                       bg=BG, fg=MUTED, font=("Segoe UI", 8, "bold"))
        lbl.pack(fill="x", pady=pady, anchor="w")
        return lbl

    #button template
    def buttonTemplate(self, parent, text, cmd, fg=TEXT, bg=CARD, font=("Segoe UI", 9)):
        return tk.Button(
            parent,
            text=text,
            fg=fg,
            font=font,  # now dynamic
            relief="flat",
            cursor="hand2",
            activebackground=bg,
            activeforeground=fg,
            command=cmd,
            bg=bg,
            padx=8,
            pady=4
        )
        

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

    # Adding Process Function
    def addProcessFunction(self):
        idx = len(self.proc_rows)
        pid = f"P{idx+1}"
        row = tk.Frame(self.proc_frame, bg=BG)
        row.pack(fill="x", pady=5)
 
        # Random Color Selection
        color = processColors[idx % len(processColors)]
        tk.Label(row, text="█", bg=BG, fg=color,
                 font=("Segoe UI", 12), width=2).pack(side="left")
 
        #Initial Values
        at_v  = tk.StringVar(value="0") 
        bt_v  = tk.StringVar(value="1")
        pri_v = tk.StringVar(value="0")
 
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
        

        tk.Button(row, text="─", fg=ERROR, bg=BG, bd=0, padx=20, cursor="hand2", command=lambda r=row, item=(pid, at_v, bt_v, pri_v, row): 
            self.removeProcess(r, item)).pack(side="right", padx=5)
    
    # function for removing process
    def removeProcess(self, r, item):
        if len(self.proc_rows) <= 3:
            messagebox.showwarning("Minimum", "At least 3 processes required.")
            return
        r.destroy()
        self.proc_rows.remove(item)

    # function for reseting all process
    def resetProcess(self):
        
        # destroy all existing rows
        for _, _, _, _, row in self.proc_rows:
            row.destroy()
 
        # clear the process list
        self.proc_rows.clear()
 
        # recreate initial 3 processes (default values)
        for i in range(3):
            self.addProcessFunction()
    
        # reset Gantt chart
        self.initializeGantt()
 
        # reset summary stats
        self._update_stat(self.averageTATContainer, "—")
        self._update_stat(self.averageWTContainer,  "—")
        self._update_stat(self.algoUsed,     "—")
        self._update_stat(self.processCount, "—")
 
        # clear results table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # reset the process input
        self.numberProcessValue.set(3)
        
        # reset the algorithm chose
        self.algoSelected.set("FCFS")
        self.priorityContainer.pack_forget()
        self.quantumContainer.pack_forget()
        

    # generate process function based from user input
    def generateProcessFunctioj(self):
        try:
            n = int(self.numberProcessValue.get())
            if n < 3:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Input Error", "Please enter a valid number of processes (≥ 3).")
            return

        # delete all existing rows process
        for _, _, _, _, row in self.proc_rows:
            row.destroy()
        self.proc_rows.clear()

        # add new rows
        for _ in range(n):
            self.addProcessFunction()

    # clear process values function
    def clearValuesFunction(self):
        for _, pid_v, at_v, bt_v, _ in self.proc_rows:
            pid_v.set(0)
            at_v.set(1)
            bt_v.set(0)
            

    # Algorithm Visibility
    def changeAlgo(self, _=None):
        algo = self.algoSelected.get()
        involvesQuantum   = algo in ("Round Robin", "Priority + RR", "Run All")
        involvesPriority   = algo in ("Priority (NP)", "Priority (P)", "Priority + RR", "Run All")

        if involvesQuantum:
            self.quantumContainer.pack(fill="x", padx=10, pady=(4,0)) # if needs quantum, this section shows
        else:
            self.quantumContainer.pack_forget() #if not, it will hide

        if involvesPriority:
            self.priorityContainer.pack(fill="x", padx=10, pady=(4,8)) # if needs ppriority, this section shows
        else:
            self.priorityContainer.pack_forget() #if not, it will hide
            self.quantumContainer.pack_configure(pady=(4,8)) if involvesQuantum else None 

    # Run application function
    def runApp(self):
        
        # Parse processes
        processes = []
        
        for i, (pid, at_v, bt_v, pri_v, _) in enumerate(self.proc_rows): # loop in process list to get all process
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

        algo    = self.algoSelected.get()
        quantum = self.quantumValue.get()
        defaultPriority     = self.priorityValue.get() == "Higher = Higher Priority" # Default Value:Higher number = Highest Priority

        # Assign colors
        self.color_map = {p["pid"]: processColors[i % len(processColors)]
                          for i, p in enumerate(processes)}

        # Run based on chosen algorithm
        if algo == "FCFS":
            gantt, results = solveFCFS(processes)
            self.showOutputs(gantt, results, "First-Come, First-Served")  # if FCFS is chosen

        elif algo == "SJF":
            gantt, results = solveSJF(processes)
            self.showOutputs(gantt, results, "Shortest Job First (NP)")  # if SJF is chosen

        elif algo == "SRT":
            gantt, results = solveSRT(processes)
            self.showOutputs(gantt, results, "Shortest Remaining Time")  # if SRT is chosen
 
        elif algo == "Round Robin":
            gantt, results = solveRoundRobin(processes, quantum)
            self.showOutputs(gantt, results, f"Round Robin (q={quantum})")  # if RR is chosen
 
        elif algo == "Priority (NP)":
            gantt, results = run_priority_np(processes, defaultPriority)  # if PRIORITY NP is chosen
            mode = "High>Hi" if defaultPriority else "Low>Hi"
            self.showOutputs(gantt, results, f"Priority NP ({mode})")

        elif algo == "Priority (P)": 
            gantt, results = run_priority_p(processes, defaultPriority)  # if PRIORITY P is chosen
            mode = "High>Hi" if defaultPriority else "Low>Hi"
            self.showOutputs(gantt, results, f"Priority Preemptive ({mode})")

        elif algo == "Priority + RR":
            gantt, results = run_priority_rr(processes, quantum, defaultPriority)  # if PRIOTIY  W RR is chosen
            mode = "High>Hi" if defaultPriority else "Low>Hi" 
            self.showOutputs(gantt, results, f"Priority+RR q={quantum} ({mode})")

        elif algo == "Run All":
            self.runAllAlgorithm(processes, quantum, defaultPriority)  # Run all and show combined in a new window

    # function for displaying gantt chart,result table, and summary
    def showOutputs(self, gantt, results, title):
        self.buildGanttChart(gantt) 
        self._fill_table(results)
        n = len(results)
        avg_tat = sum(r["tat"] for r in results) / n
        avg_wt  = sum(r["wt"]  for r in results) / n
        self._update_stat(self.averageTATContainer, f"{avg_tat:.2f}")
        self._update_stat(self.averageWTContainer,  f"{avg_wt:.2f}")
        self._update_stat(self.algoUsed, f"{self.algoSelected.get()}")
        self._update_stat(self.processCount, f"{n}")

    # Iniatilize Gantt Chart
    def initializeGantt(self):
        c = self.gantt_canvas
        c.delete("all")
        c.create_text(400, 80,
                      text="-",
                      fill=MUTED, font=("Segoe UI", 11), anchor="center")

    # Build Gantt Chart
    def buildGanttChart(self, gantt):
        c = self.gantt_canvas
        c.delete("all")  # Clear previous drawings on the canvas
        
        # If no data, nothing to draw
        if not gantt:
            return

        # Constants Value for layout
        BLOCK_H  = 44      
        LABEL_H  = 24      
        TIMELINE = 18      
        TOP      = 20      
        PX_PER_T = 38      

        # Get total time from last segment
        total_end = gantt[-1]["end"]

        # Set canvas width 
        canvas_w  = max(total_end * PX_PER_T + 80, 600)

        # Define scrollable area of canvas
        c.configure(scrollregion=(0, 0, canvas_w, BLOCK_H + LABEL_H + TIMELINE + TOP + 30))

        for t in range(total_end + 1):
            x = 40 + t * PX_PER_T  # Convert time → pixel position

            # Small vertical tick line
            c.create_line( x, TOP + BLOCK_H, x, TOP + BLOCK_H + 6, fill=MUTED, width=1)

            # Time label below the tick
            c.create_text(x, TOP + BLOCK_H + TIMELINE, text=str(t), fill=MUTED, font=("Consolas", 8), anchor="center")

        # Draw Gantt Chart BLOCKS
        for seg in gantt:
            # Convert start/end time → pixel positions
            x1 = 40 + seg["start"] * PX_PER_T
            x2 = 40 + seg["end"]   * PX_PER_T

            y1 = TOP
            y2 = TOP + BLOCK_H

            pid   = seg["pid"]                     # Process ID (e.g., P1)
            color = self.color_map.get(pid, ACCENT)  # Color per process

            # Draw rectangle block for this segment
            c.create_rectangle(x1, y1, x2, y2, fill=color, outline=BG,width=2)

            # Draw process label inside block 
            bw = x2 - x1  
            if bw > 20:   
                c.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text=pid,
                    fill="white",
                    font=("Segoe UI", 9, "bold"),
                    anchor="center"
                )

        # Draw "CPU" label on the left side
        c.create_text(32, TOP + BLOCK_H // 2, text="CPU", fill=MUTED, font=("Segoe UI", 8, "bold"), anchor="e")
     
    #End of Gantt Chartt 
        
    # Results Table Section
    def _fill_table(self, results):
        
        for item in self.tree.get_children(): #clear existing rows in the table
            self.tree.delete(item)
            
        for i, r in enumerate(sorted(results, key=lambda x: int(x["pid"][1:]))): #insert new sorted rows
            
            tag = ("alt",) if i % 2 else () #alternate color for each row
            
            self.tree.insert("", "end", values=(r["pid"], r["at"], r["bt"], r["priority"],r["finish"], r["tat"], r["wt"]), tags=tag) #inserts to table
            
            # Color the PID cell using a tag
            pid_tag = f"pid_{r['pid']}"
            color = self.color_map.get(r["pid"], ACCENT)
            self.tree.tag_configure(pid_tag, foreground=color)

    # Function when Run All Algorithm is Selected
    def runAllAlgorithm(self, processes, quantum, defaultPriority):
        #initialize new window for all algorithm
        allAlgoWindow = tk.Toplevel(self)
        allAlgoWindow.title("All Algorithms — Comparison")
        allAlgoWindow.configure(bg=BG)
        allAlgoWindow.geometry("1100x750")

        tk.Label(allAlgoWindow, text="All Algorithms Comparison",
                 bg=BG, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(pady=(16,4))
        tk.Frame(allAlgoWindow, bg=BORDER, height=1).pack(fill="x", padx=24)

        # Scrollable canvas
        outer = tk.Frame(allAlgoWindow, bg=BG)
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

        mode = "High>Hi" if defaultPriority else "Low>Hi"
        listOfAlgo = [
            ("FCFS",                       solveFCFS(processes)),
            ("SJF (Non-Preemptive)",        solveSJF(processes)),
            ("SRT (Preemptive)",            solveSRT(processes)),
            (f"Round Robin (q={quantum})",  solveRoundRobin(processes, quantum)),
            (f"Priority NP ({mode})",       run_priority_np(processes, defaultPriority)),
            (f"Priority P ({mode})",        run_priority_p(processes, defaultPriority)),
            (f"Priority+RR q={quantum} ({mode})", run_priority_rr(processes, quantum, defaultPriority)),
        ]

        for name, (gantt, results) in listOfAlgo:
            n       = len(results)
            avg_tat = sum(r["tat"] for r in results) / n
            avg_wt  = sum(r["wt"]  for r in results) / n

            sec = tk.Frame(content, bg=CARD)
            sec.pack(fill="x", expand=True, pady=6, padx=4)

            # Header
            hf = tk.Frame(sec, bg=BORDER)
            hf.pack(fill="x")
            tk.Label(hf, text=f"  {name}", bg=BORDER, fg=TEXT,
                     font=("Segoe UI", 11, "bold"), pady=6).pack(side="left")
            tk.Label(hf, text=f"Avg TAT: {avg_tat:.2f}  |  Avg WT: {avg_wt:.2f}  ",
                     bg=BORDER, fg=ACCENT2,
                     font=("Segoe UI", 10)).pack(side="right")

            # Mini Gantt Chart
            mini = tk.Canvas(sec, bg=CARD, height=80, highlightthickness=0)
            mini.pack(fill="x", expand=True, padx=8, pady=6)
            self.buildAllAlgoGanttChart(mini, gantt)

            # Mini Table Sumamry
            cols = ("pid","at","bt","finish","tat","wt")
            tr = ttk.Treeview(sec, columns=cols, show="headings",
                              height=len(results), selectmode="none")
            for col, lbl, w in [("pid","PID",50),("at","AT",60),("bt","BT",55),
                                  ("finish","Finish",65),("tat","TAT",60),("wt","WT",60)]:
                tr.heading(col, text=lbl); tr.column(col, width=w, anchor="center")
            for i, r in enumerate(sorted(results, key=lambda x: int(x["pid"][1:]))):
                tag = ("alt",) if i%2 else ()
                tr.insert("", "end", values=(r["pid"],r["at"],r["bt"],
                                              r["finish"],r["tat"],r["wt"]), tags=tag)
            tr.tag_configure("alt", background="#1e2235")
            tr.pack(fill="x", padx=8, pady=(0,8))

    #function for building gantt chart for all algo
    def buildAllAlgoGanttChart(self, canvas, gantt):
        """Compact Gantt for the Run All window."""
        canvas.update_idletasks()
        W = canvas.winfo_width() 
        if W <= 1:
             W = 900  # fallback

        total = gantt[-1]["end"] if gantt else 1
        scale = max(40, (W - 80) / total)
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


