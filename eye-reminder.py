# -*- coding: utf-8 -*-
"""
20-20-20 Eye Reminder - TEST MODE (5 sec interval, 5 sec countdown)
Requirements: pip install pystray pillow
"""

import threading
import time
import tkinter as tk
from tkinter import font as tkfont
import sys

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# ---- CONFIG (test mode) ----
TEST_MODE = True
INTERVAL_SECONDS = 5 if TEST_MODE else 20 * 60
BREAK_SECONDS = 5 if TEST_MODE else 20

stop_event = threading.Event()
tray_icon = None


def play_alarm():
    def _play():
        if HAS_WINSOUND:
            for _ in range(6):
                if stop_event.is_set():
                    break
                winsound.Beep(1000, 300)
                time.sleep(0.1)
                winsound.Beep(1400, 300)
                time.sleep(0.1)
        else:
            print("\a\a\a")
    threading.Thread(target=_play, daemon=True).start()


def show_popup():
    result = {"action": None}
    root = tk.Tk()
    root.withdraw()

    win = tk.Toplevel(root)
    win.title("Eye Break!")
    win.configure(bg="#0a0a0a")
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.protocol("WM_DELETE_WINDOW", lambda: None)

    W, H = 520, 380
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    remaining = {"s": BREAK_SECONDS}
    timer_running = {"v": True}
    after_id = {"id": None}

    f_big   = tkfont.Font(family="Segoe UI", size=52, weight="bold")
    f_title = tkfont.Font(family="Segoe UI", size=16, weight="bold")
    f_sub   = tkfont.Font(family="Segoe UI", size=11)
    f_btn   = tkfont.Font(family="Segoe UI", size=12, weight="bold")

    tk.Label(win, text="EYE BREAK", font=f_title,
             fg="#ff4444", bg="#0a0a0a").pack(pady=(28, 2))

    tk.Label(win, text="Look at something 20 feet away for:",
             font=f_sub, fg="#888888", bg="#0a0a0a").pack()

    count_var = tk.StringVar(value=str(BREAK_SECONDS))
    count_lbl = tk.Label(win, textvariable=count_var, font=f_big,
                         fg="#ffffff", bg="#0a0a0a")
    count_lbl.pack(pady=8)

    tk.Label(win, text="seconds", font=f_sub,
             fg="#555555", bg="#0a0a0a").pack()

    bar_canvas = tk.Canvas(win, width=380, height=8, bg="#1a1a1a",
                           highlightthickness=0)
    bar_canvas.pack(pady=12)
    bar_rect = bar_canvas.create_rectangle(0, 0, 380, 8, fill="#ff4444", outline="")

    status_var = tk.StringVar(value="Keep your eyes on the distance...")
    tk.Label(win, textvariable=status_var, font=f_sub,
             fg="#666666", bg="#0a0a0a").pack(pady=(0, 16))

    btn_frame = tk.Frame(win, bg="#0a0a0a")
    btn_frame.pack(pady=4)

    continue_btn = tk.Button(
        btn_frame, text="Continue Working", font=f_btn,
        bg="#1a1a1a", fg="#444444", relief="flat",
        padx=24, pady=10, cursor="arrow",
        state="disabled",
        command=lambda: _action("continue")
    )
    continue_btn.grid(row=0, column=0, padx=10)

    stop_btn = tk.Button(
        btn_frame, text="Stop Reminders", font=f_btn,
        bg="#1a1a1a", fg="#555555", relief="flat",
        padx=24, pady=10, cursor="hand2",
        command=lambda: _action("stop")
    )
    stop_btn.grid(row=0, column=1, padx=10)

    def tick():
        if not timer_running["v"]:
            return
        remaining["s"] -= 1
        count_var.set(str(max(remaining["s"], 0)))
        pct = max(remaining["s"], 0) / BREAK_SECONDS
        bar_canvas.coords(bar_rect, 0, 0, int(380 * pct), 8)

        if remaining["s"] <= 0:
            timer_running["v"] = False
            count_var.set("OK")
            count_lbl.configure(fg="#44ff88")
            bar_canvas.itemconfig(bar_rect, fill="#44ff88")
            bar_canvas.coords(bar_rect, 0, 0, 380, 8)
            status_var.set("Great job! Click Continue to resume.")
            continue_btn.configure(
                state="normal", bg="#003322", fg="#44ff88", cursor="hand2"
            )
        else:
            after_id["id"] = win.after(1000, tick)

    def _action(action):
        timer_running["v"] = False
        if after_id["id"]:
            win.after_cancel(after_id["id"])
        result["action"] = action
        win.destroy()
        root.destroy()

    win.after(1000, tick)
    play_alarm()
    root.mainloop()
    return result["action"] == "continue"


def reminder_loop():
    mode = "TEST" if TEST_MODE else "PROD"
    print(f"[eye_reminder] Started ({mode} mode). Popup in {INTERVAL_SECONDS}s.")
    while not stop_event.is_set():
        for _ in range(INTERVAL_SECONDS):
            if stop_event.is_set():
                return
            time.sleep(1)

        if stop_event.is_set():
            return

        should_continue = show_popup()
        if not should_continue:
            print("[eye_reminder] Stopped by user.")
            stop_event.set()
            sys.exit(0)


def make_tray_image():
    img = Image.new("RGB", (64, 64), color="#0a0a0a")
    d = ImageDraw.Draw(img)
    d.ellipse([8, 20, 56, 44], outline="#ff4444", width=4)
    d.ellipse([24, 26, 40, 38], fill="#ff4444")
    return img


def start_tray():
    global tray_icon

    def on_quit(icon, item):
        stop_event.set()
        icon.stop()
        sys.exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("Eye Reminder - Running", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit),
    )
    tray_icon = pystray.Icon("eye_reminder", make_tray_image(), "Eye Reminder", menu)
    tray_icon.run()


if __name__ == "__main__":
    loop_thread = threading.Thread(target=reminder_loop, daemon=True)
    loop_thread.start()

    if HAS_TRAY:
        print("[eye_reminder] Tray icon active. Right-click to quit.")
        start_tray()
    else:
        print("[eye_reminder] No tray. Press Ctrl+C to stop.")
        try:
            loop_thread.join()
        except KeyboardInterrupt:
            stop_event.set()
