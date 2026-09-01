#!/usr/bin/env python3
"""
==============================================================================
POWER_PULSE // Windows Live Floating Glass HUD Widget (Zero-Dependency)
Developed for Yahia Bin Zaman
==============================================================================
"""
import sys
import os
import json
import time
import urllib.request
import tkinter as tk
from tkinter import font as tkfont

API_URL = "http://127.0.0.1:8765/api/telemetry"

class PowerPulseHUD(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PowerPulse Live HUD")
        self.overrideredirect(True) # Frameless window
        self.attributes("-topmost", True) # Always on top
        try:
            self.attributes("-alpha", 0.93) # Glass translucency
        except Exception:
            pass

        self.configure(bg="#0a0e14")
        self.geometry("340x260+100+100")
        self.resizable(False, False)

        # Dragging variables
        self._drag_data = {"x": 0, "y": 0}
        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)
        self.bind("<B1-Motion>", self.do_drag)

        # Double click to open Web Dashboard
        self.bind("<Double-Button-1>", lambda e: os.system("start http://127.0.0.1:8765"))

        # Right click to close
        self.bind("<Button-3>", lambda e: self.destroy())

        self.build_ui()
        self.poll_telemetry()

    def build_ui(self):
        # Outer border frame with glowing neon cyan/emerald highlight
        self.border_frame = tk.Frame(self, bg="#00ff66", bd=1)
        self.border_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.inner_frame = tk.Frame(self.border_frame, bg="#0b1017", padx=12, pady=10)
        self.inner_frame.pack(fill="both", expand=True)

        # Header Title & Status
        hdr_frame = tk.Frame(self.inner_frame, bg="#0b1017")
        hdr_frame.pack(fill="x", pady=(0, 6))

        self.lbl_title = tk.Label(
            hdr_frame, text="⚡ POWER_PULSE // LIVE HUD",
            font=("Segoe UI", 10, "bold"), fg="#00f0ff", bg="#0b1017"
        )
        self.lbl_title.pack(side="left")

        self.lbl_dot = tk.Label(
            hdr_frame, text="● LIVE",
            font=("Segoe UI", 8, "bold"), fg="#00ff66", bg="#0b1017"
        )
        self.lbl_dot.pack(side="right")

        # Main Power Metric Box
        self.pwr_frame = tk.Frame(self.inner_frame, bg="#111822", bd=1, relief="solid", padx=8, pady=6)
        self.pwr_frame.pack(fill="x", pady=(0, 6))

        self.lbl_watts = tk.Label(
            self.pwr_frame, text="14.8 W",
            font=("Segoe UI", 18, "bold"), fg="#00ff66", bg="#111822"
        )
        self.lbl_watts.pack(side="left")

        self.lbl_cost_hr = tk.Label(
            self.pwr_frame, text="৳ 0.208 / hr\nPeak: 45.2W",
            font=("Segoe UI", 8), fg="#8fa0b5", bg="#111822", justify="right"
        )
        self.lbl_cost_hr.pack(side="right")

        # Hardware Utilization (CPU, GPU, RAM)
        self.hw_frame = tk.Frame(self.inner_frame, bg="#0b1017")
        self.hw_frame.pack(fill="x", pady=(0, 6))

        self.lbl_cpu = tk.Label(self.hw_frame, text="CPU: 24%  [■■······]", font=("Consolas", 8), fg="#00f0ff", bg="#0b1017")
        self.lbl_cpu.pack(anchor="w")

        self.lbl_gpu = tk.Label(self.hw_frame, text="GPU: 12%  [■·······]", font=("Consolas", 8), fg="#b026ff", bg="#0b1017")
        self.lbl_gpu.pack(anchor="w")

        self.lbl_ram = tk.Label(self.hw_frame, text="RAM: 58%  [■■■■■···]", font=("Consolas", 8), fg="#ffb000", bg="#0b1017")
        self.lbl_ram.pack(anchor="w")

        # Network & Daily Billing
        self.bot_frame = tk.Frame(self.inner_frame, bg="#0b1017")
        self.bot_frame.pack(fill="x", pady=(0, 2))

        self.lbl_net = tk.Label(self.bot_frame, text="Net: 1.8 Mbps | Ping: 2.0ms", font=("Segoe UI", 8), fg="#c0d0e0", bg="#0b1017")
        self.lbl_net.pack(anchor="w")

        self.lbl_data_today = tk.Label(self.bot_frame, text="Today Data: 1.45 GB | Bill: ৳ 0.35", font=("Segoe UI", 8, "bold"), fg="#00ff66", bg="#0b1017")
        self.lbl_data_today.pack(anchor="w")

        # Footer hints
        self.lbl_hint = tk.Label(
            self.inner_frame, text="Drag to move • Double-click for Cockpit • Right-click to exit",
            font=("Segoe UI", 7), fg="#405060", bg="#0b1017"
        )
        self.lbl_hint.pack(side="bottom", pady=(4, 0))

    def make_meter(self, pct, length=8):
        clamped = max(0.0, min(100.0, pct))
        filled = int(round((clamped / 100.0) * length))
        empty = max(0, length - filled)
        return "[" + ("■" * filled) + ("·" * empty) + "]"

    def poll_telemetry(self):
        try:
            req = urllib.request.Request(API_URL, headers={"User-Agent": "PowerPulse-HUD"})
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.update_data(data)
        except Exception:
            self.lbl_watts.config(text="-- W")
            self.lbl_dot.config(text="● SYNC", fg="#ffb000")

        self.after(1000, self.poll_telemetry)

    def update_data(self, data):
        p = data.get("power", {})
        total_w = p.get("total_watts", 0.0)
        peak_w = p.get("peak_watts", 0.0)
        cost_hr = (total_w / 1000.0) * 25.00

        cpu = data.get("cpu_usage_pct", 0.0)
        gpu = data.get("gpu_usage_pct", 8.0)
        ram = data.get("ram", {})
        ram_pct = ram.get("pct", 55.0)

        net = data.get("network", {})
        down_mbps = net.get("down_mbps", 0.0)
        ping_ms = net.get("ping_ms", 2.0)

        hist = data.get("history", {})
        today_data = hist.get("today", {}).get("data_formatted", "0 MB")
        today_cost = hist.get("today", {}).get("cost", 0.0)

        self.lbl_watts.config(text=f"{total_w:.1f} W")
        self.lbl_cost_hr.config(text=f"৳ {cost_hr:.3f} / hr\nPeak: {peak_w:.1f}W")
        self.lbl_dot.config(text="● LIVE", fg="#00ff66")

        self.lbl_cpu.config(text=f"CPU: {cpu:>4.1f}%  {self.make_meter(cpu)}")
        self.lbl_gpu.config(text=f"GPU: {gpu:>4.1f}%  {self.make_meter(gpu)}")
        self.lbl_ram.config(text=f"RAM: {ram_pct:>4.1f}%  {self.make_meter(ram_pct)}")

        self.lbl_net.config(text=f"Net: {down_mbps:.2f} Mbps | Ping: {ping_ms:.1f}ms")
        self.lbl_data_today.config(text=f"Today Data: {today_data} | Bill: ৳ {today_cost:.2f}")

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def stop_drag(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def do_drag(self, event):
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = PowerPulseHUD()
    app.mainloop()
