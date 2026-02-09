import random, time, threading, csv, os
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pyttsx3

# ================= VOICE =================
engine = pyttsx3.init()
engine.setProperty('rate', 145)

def speak(msg):
    threading.Thread(
        target=lambda:(engine.say(msg),engine.runAndWait()),
        daemon=True
    ).start()

# ================= SENSOR =================
def read_temperature(): return random.randint(200,700)
def read_pressure(): return random.randint(10,100)
def read_vibration(): return random.randint(0,120)
def read_radiation(): return random.randint(0,50)

# ================= THRESHOLDS =================
TH = {"t":600,"p":20,"v":90,"r":40}

# ================= AI =================
def risk_engine(t,p,v,r):
    risk = 0
    if t>TH["t"]: risk+=25
    if p<TH["p"]: risk+=25
    if v>TH["v"]: risk+=25
    if r>TH["r"]: risk+=25

    if risk>=75: return "🚨 CRITICAL", risk, "ABORT MISSION"
    if risk>=50: return "⚠ HIGH RISK", risk, "ACTIVATE SHIELD"
    if risk>=25: return "🟡 WARNING", risk, "STABILIZE SYSTEM"
    return "✅ SAFE", risk, "CONTINUE MISSION"

# ================= GUI =================
root = tk.Tk()
root.title("🚀  DEVANSH QUANTUM NAVIGATOR")
root.geometry("1800x950")
root.configure(bg="#0b0e1a")

root.after(1000, lambda:speak(" WELCOME TO THE DEVANSH MITTAL TECHNICAL WORLD."))

left = tk.Frame(root,bg="#0b0e1a")
left.pack(side=tk.LEFT,fill=tk.Y,padx=10)

right = tk.Frame(root,bg="#0b0e1a")
right.pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)

# ================= CONTROLLER =================
ctrl = tk.LabelFrame(left,text="Controller Inputs",
                     fg="#00ffdd",bg="#0b0e1a")
ctrl.pack(pady=6)

ctrl_vars = {
    "Temp °C":tk.StringVar(value="320"),
    "Pressure":tk.StringVar(value="55"),
    "Vibration":tk.StringVar(value="35"),
    "Radiation":tk.StringVar(value="15")
}

for i,(k,v) in enumerate(ctrl_vars.items()):
    tk.Label(ctrl,text=k,fg="#00ffdd",bg="#0b0e1a").grid(row=i,column=0)
    tk.Entry(ctrl,textvariable=v,width=6).grid(row=i,column=1)

# ================= STATUS BOX HELPER =================
def status_box(title,color):
    box = tk.LabelFrame(left,text=title,fg=color,bg="#0b0e1a")
    box.pack(pady=6,fill="x")
    var = tk.StringVar()
    tk.Label(box,textvariable=var,fg=color,bg="#0b0e1a",
             font=("Consolas",11,"bold"),
             justify="left").pack()
    return var

curr_var = status_box("CURRENT STATUS","#ff5555")
pred_var = status_box("PREDICTED STATUS","#ffaa00")
heal_var = status_box("AUTO HEAL SYSTEM","#00ff88")
cyber_var = status_box("CYBER STATUS","#ff0000")

# ================= 🔥 NEW VISIBLE CONTROLS =================
tk.Label(left,text="MISSION MODE",
         fg="#00ffaa",bg="#0b0e1a",
         font=("Consolas",10,"bold")).pack(pady=(10,0))

mission_var = tk.StringVar(value="DEFENCE")
tk.OptionMenu(left, mission_var,
              "SATELLITE","DRONE","DEFENCE","MISSILE").pack()

tk.Label(left,text="FAILURE SIMULATION",
         fg="#ff7777",bg="#0b0e1a",
         font=("Consolas",10,"bold")).pack(pady=(10,0))

failure_var = tk.StringVar(value="NONE")
tk.OptionMenu(left, failure_var,
              "NONE","ENGINE","RADIATION","SPOOF").pack()

mode_info = tk.StringVar()
fail_info = tk.StringVar()
tk.Label(left,textvariable=mode_info,
         fg="#00ffdd",bg="#0b0e1a").pack()
tk.Label(left,textvariable=fail_info,
         fg="#ff9999",bg="#0b0e1a").pack()

# ================= FIGURES =================
fig = Figure(figsize=(11,9))
ax_c = fig.add_subplot(221)
ax_p = fig.add_subplot(222)
ax_c3 = fig.add_subplot(223,projection="3d")
ax_p3 = fig.add_subplot(224,projection="3d")

canvas = FigureCanvasTkAgg(fig,master=right)
canvas.get_tk_widget().pack(fill=tk.BOTH,expand=True)

cur = {"t":[],"p":[],"v":[],"r":[]}
pre = {"t":[],"p":[],"v":[],"r":[]}
last_voice = ""

def safe_int(var):
    try: return int(var.get())
    except: return 0

# ================= MAIN LOOP =================
def loop():
    global last_voice
    while True:
        t,p,v,r = read_temperature(),read_pressure(),read_vibration(),read_radiation()

        # ===== FAILURE EFFECT =====
        if failure_var.get()=="ENGINE":
            t+=150; p-=30; v+=50
        elif failure_var.get()=="RADIATION":
            r+=35
        elif failure_var.get()=="SPOOF":
            t,p,v,r = 999,1,200,99

        cs,cr,cd = risk_engine(t,p,v,r)

        # ===== MODE EFFECT =====
        mode_boost = {"SATELLITE":5,"DRONE":10,"DEFENCE":15,"MISSILE":25}
        cr = min(100, cr + mode_boost[mission_var.get()])

        # ===== AUTO HEAL =====
        if cr>=75: heal="ENGINE LOCKED | ABORT"
        elif cr>=50: heal="SHIELD + COOLING ACTIVE"
        elif cr>=25: heal="AUTO STABILIZING"
        else: heal="SYSTEM NORMAL"

        # ===== CYBER =====
        cyber = "⚠ SPOOF ATTACK" if (t>900 or v>180 or r>80) else "NORMAL"

        curr_var.set(
            f"{cs} ({cr}%)\n"
            f"🌡 {t} °C\n⛽ {p}\n⚙ {v}\n☢ {r}\n"
            f"🤖 ACTION: {cd}"
        )
        heal_var.set(heal)
        cyber_var.set(cyber)

        mode_info.set(f"MODE: {mission_var.get()}")
        fail_info.set(f"FAILURE: {failure_var.get()}")

        if cr>=50 and cs!=last_voice:
            speak(cs); last_voice=cs

        pt,pp,pv,pr = [safe_int(x) for x in ctrl_vars.values()]
        ps,prk,pd = risk_engine(pt,pp,pv,pr)

        pred_var.set(
            f"{ps} ({prk}%)\n"
            f"🌡 {pt} °C\n⛽ {pp}\n⚙ {pv}\n☢ {pr}\n"
            f"🤖 ACTION: {pd}"
        )

        for k,val in zip(cur,[t,p,v,r]): cur[k].append(val)
        for k,val in zip(pre,[pt,pp,pv,pr]): pre[k].append(val)

        ax_c.clear()
        ax_c.plot(cur["t"],label="Temp")
        ax_c.plot(cur["p"],label="Pressure")
        ax_c.plot(cur["v"],label="Vibration")
        ax_c.plot(cur["r"],label="Radiation")
        ax_c.legend(); ax_c.set_title("CURRENT")

        ax_p.clear()
        ax_p.plot(pre["t"],label="Temp")
        ax_p.plot(pre["p"],label="Pressure")
        ax_p.plot(pre["v"],label="Vibration")
        ax_p.plot(pre["r"],label="Radiation")
        ax_p.legend(); ax_p.set_title("PREDICTED")

        ax_c3.clear()
        ax_c3.scatter(random.uniform(-5,5),
                      random.uniform(-5,5),
                      random.uniform(0,20),s=100)

        ax_p3.clear()
        ax_p3.scatter(pt/100,pp/10,pv/10,s=100)

        canvas.draw()
        time.sleep(1)

threading.Thread(target=loop,daemon=True).start()
root.mainloop()