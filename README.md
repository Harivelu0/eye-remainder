# eye-reminder

A lightweight Python app that enforces the **20-20-20 rule** for eye health on Windows.

Every 20 minutes, a blocking popup appears with a loud alarm. You cannot dismiss it until a 20-second countdown finishes. No cheating.

---

## Why

The 20-20-20 rule says: every 20 minutes, look at something 20 feet away for 20 seconds. Every reminder app I tried was too easy to dismiss. This one isn't.

---

## Demo

```
[20 min timer] --> ALARM fires --> Blocking popup appears
                                        |
                                   20-sec countdown
                                        |
                               "Continue" button unlocks
                                        |
                              Click Continue --> back to work
                              Click Stop    --> session ends
```

---

## Features

- Runs silently in the **system tray**
- **Loud beeping alarm** on every trigger (no audio files needed)
- Popup is **always-on-top** and the X button is disabled
- **"Continue" button locked** until full 20-second countdown completes
- System tray icon with right-click **Quit** option
- Built-in **test mode** (5-sec interval) for quick verification

---

## Requirements

- Windows
- Python 3.8+
- `pystray` and `Pillow` (for system tray icon)

Core functionality (popup + alarm) works with zero installs. Tray icon needs the two packages below.

---

## Installation

```bash
pip install pystray pillow
```

---

## Usage

```bash
python eye_reminder.py
```

The app starts immediately. Popup fires after 20 minutes.

### Test mode

To verify it works before committing to 20-minute waits, set `TEST_MODE = True` at the top of the file:

```python
TEST_MODE = True   # popup fires in 5 seconds, countdown is 5 seconds
```

Flip back to `False` for normal use.

---

## Auto-start on Windows boot

### Option A — Manual (2 steps)

1. Press `Win+R`, type `shell:startup`, press Enter
2. Create a shortcut in that folder pointing to:
   ```
   pythonw C:\path\to\eye_reminder.py
   ```
   Using `pythonw` hides the terminal window.

### Option B — Automated script

Download `write_shortcut.py` from this repo and run:

```bash
# Step 1: generates the PowerShell setup script
python write_shortcut.py

# Step 2: creates the startup shortcut
powershell -ExecutionPolicy Bypass -File "C:\Users\<you>\EyeReminder\make_shortcut.ps1"
```

---

## Project structure

```
eye-reminder/
├── eye_reminder.py       # main app
├── write_shortcut.py     # helper: creates Windows startup shortcut
└── README.md
```

---

## How it works

**Blocking the close button**

```python
win.protocol("WM_DELETE_WINDOW", lambda: None)
```

Overrides the X button with a no-op. The window cannot be closed until you click a button.

**Locked Continue button**

```python
continue_btn = tk.Button(..., state="disabled")

def tick():
    remaining["s"] -= 1
    if remaining["s"] <= 0:
        continue_btn.configure(state="normal", fg="#44ff88")
    else:
        win.after(1000, tick)
```

Button stays grey and unclickable until the countdown hits zero.

**Alarm (no audio files)**

```python
import winsound

for _ in range(6):
    winsound.Beep(1000, 300)
    time.sleep(0.1)
    winsound.Beep(1400, 300)
    time.sleep(0.1)
```

Uses the Windows built-in `winsound` module. No mp3, no wav, no external deps.

---

## Configuration

At the top of `eye_reminder.py`:

| Variable | Default | Description |
|---|---|---|
| `TEST_MODE` | `False` | Set `True` for 5-sec test intervals |
| `INTERVAL_SECONDS` | `20 * 60` | Time between popups (seconds) |
| `BREAK_SECONDS` | `20` | Countdown duration (seconds) |

---

## Dependencies

| Package | Required | Purpose |
|---|---|---|
| `tkinter` | Yes (built-in) | Popup UI |
| `winsound` | Yes (built-in) | Alarm beeps |
| `threading` | Yes (built-in) | Background timer |
| `pystray` | Optional | System tray icon |
| `Pillow` | Optional | Tray icon image |

---

## License

MIT
