#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
⚡ POWER_PULSE // CYBER_VOLT v4.2 ⚡
High-Voltage Energy Grid, Quantum Core Monitor & Cyber Telemetry Engine
==============================================================================
"""

import time
import random
import sys
import os
import math
import datetime
import shutil

# ANSI Color & Style Palettes
GREEN = "\033[92m"
BRIGHT_GREEN = "\033[1;32m"
DARK_GREEN = "\033[32m"
CYAN = "\033[96m"
BRIGHT_CYAN = "\033[1;36m"
RED = "\033[91m"
BRIGHT_RED = "\033[1;31m"
YELLOW = "\033[93m"
BRIGHT_YELLOW = "\033[1;33m"
MAGENTA = "\033[95m"
BRIGHT_MAGENTA = "\033[1;95m"
WHITE = "\033[97m"
GRAY = "\033[90m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

from hardware_monitor import HardwareDetector

detector = HardwareDetector()

class EnergyTracker:
    def __init__(self):
        self.start_time = time.time()
        self.last_update = time.time()
        self.detector = detector
        self.cumulative_kwh = 0.0015
        self.surge_level = 0.0
        self.active_pulses = 1420
        self.cost_rate = 0.12 # $ / kWh
        
        # Initial telemetry
        hw = self.detector.get_realtime_power()
        self.current_watts = hw["total_watts"]
        self.monitor_watts = hw["monitor_watts"]
        self.system_watts = hw["system_watts"]
        self.voltage = hw["voltage"]
        self.current_amps = hw["current_amps"]
        self.grid_load_pct = 42.0
        self.core_temp_c = 41.5
        
    def tick(self, activity_multiplier=1.0):
        now = time.time()
        dt = max(0.001, now - self.last_update)
        self.last_update = now
        
        hw = self.detector.get_realtime_power()
        
        # Calculate dynamic fluctuations with activity multiplier & surge
        self.monitor_watts = hw["monitor_watts"] * (1.0 + self.surge_level * 0.4)
        self.system_watts = hw["system_watts"] * activity_multiplier * (1.0 + self.surge_level * 1.5)
        self.current_watts = self.monitor_watts + self.system_watts
        
        # Voltage & current
        self.voltage = hw["voltage"] + (self.surge_level * 8.0)
        self.current_amps = self.current_watts / max(1.0, self.voltage)
        
        # Energy accumulation: kWh = (Watts * hours)
        hours = dt / 3600.0
        self.cumulative_kwh += (self.current_watts / 1000.0) * hours
        
        # Load % and Temperature
        self.grid_load_pct = min(99.9, (self.current_watts / 120.0) * 100.0)
        self.core_temp_c = 36.0 + (self.grid_load_pct * 0.35) + random.uniform(-0.3, 0.3)
        self.active_pulses += random.randint(1, 4)
        
        # Decay surge slowly
        if self.surge_level > 0.05:
            self.surge_level *= 0.85
        else:
            self.surge_level = 0.0

energy_sys = EnergyTracker()

def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def get_primary_display_info():
    if detector.displays:
        d = detector.displays[0]
        return f"{d['name']} ({d['resolution']} @ {d['refresh_rate']:.0f}Hz)"
    return "Generic (1080p @ 60Hz)"

def render_power_bar(pct, length=12):
    filled = int(length * (pct / 100.0))
    filled = max(0, min(length, filled))
    empty = length - filled
    
    if pct < 45:
        bar_color = BRIGHT_GREEN
    elif pct < 75:
        bar_color = BRIGHT_YELLOW
    else:
        bar_color = BRIGHT_RED
        
    return f"{bar_color}{'█' * filled}{GRAY}{'░' * empty}{RESET} {BOLD}{bar_color}{pct:4.1f}%{RESET}"

def render_status_bar():
    energy_sys.tick()
    w = energy_sys.current_watts
    m_w = energy_sys.monitor_watts
    s_w = energy_sys.system_watts
    kwh = energy_sys.cumulative_kwh
    volts = energy_sys.voltage
    amps = energy_sys.current_amps
    temp = energy_sys.core_temp_c
    load = energy_sys.grid_load_pct
    disp_info = get_primary_display_info()
    
    # Wattage coloring
    w_col = BRIGHT_GREEN if w < 60 else (BRIGHT_YELLOW if w < 120 else BRIGHT_RED)
    temp_col = BRIGHT_GREEN if temp < 50 else (BRIGHT_YELLOW if temp < 70 else BRIGHT_RED)
    
    lines = []
    lines.append(f"{DARK_GREEN}┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐{RESET}")
    lines.append(f"{DARK_GREEN}│ {BRIGHT_CYAN}⚡ POWER_PULSE // CYBER_VOLT v4.2{RESET} {DARK_GREEN}│{RESET} {WHITE}DISPLAY:{RESET} {BRIGHT_YELLOW}{disp_info:<27}{RESET} {DARK_GREEN}│{RESET} {WHITE}SOC/GPU:{RESET} {CYAN}{detector.gpu_name:<12}{RESET} {DARK_GREEN}│{RESET} {GRAY}{now_str()}{RESET} {DARK_GREEN}│{RESET}")
    lines.append(f"{DARK_GREEN}├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤{RESET}")
    lines.append(
        f"{DARK_GREEN}│{RESET} {BOLD}{WHITE}TOTAL DRAW:{RESET} {w_col}{w:5.1f} W{RESET} "
        f"{GRAY}(Disp: {m_w:4.1f}W | Sys: {s_w:4.1f}W){RESET} "
        f"{DARK_GREEN}│{RESET} {BOLD}{WHITE}ENERGY:{RESET} {BRIGHT_MAGENTA}{kwh:7.4f} kWh{RESET} "
        f"{DARK_GREEN}│{RESET} {BOLD}{WHITE}LINE:{RESET} {BRIGHT_CYAN}{volts:5.1f}V{RESET} ({amps:4.2f}A) "
        f"{DARK_GREEN}│{RESET} {BOLD}{WHITE}TEMP:{RESET} {temp_col}{temp:4.1f}°C{RESET} "
        f"{DARK_GREEN}│{RESET} {BOLD}{WHITE}LOAD:{RESET} {render_power_bar(load, 8)} {DARK_GREEN}│{RESET}"
    )
    lines.append(f"{DARK_GREEN}└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘{RESET}")
    return "\n".join(lines)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def prompt_user(msg, default="1"):
    try:
        val = input(f"\n{BRIGHT_YELLOW}{msg}{RESET} ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        return default

def live_oscilloscope_monitor(duration_sec=12):
    clear_screen()
    print(f"{BRIGHT_CYAN}══════════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"   ⚡ {BOLD}{BRIGHT_YELLOW}REAL-TIME POWER_PULSE // VOLT OSCILLOSCOPE MONITOR{RESET} ⚡ (Press Ctrl+C to Return)")
    print(f"{BRIGHT_CYAN}══════════════════════════════════════════════════════════════════════════════════════{RESET}\n")
    
    cols = 64
    rows = 10
    start = time.time()
    t = 0.0
    
    try:
        while time.time() - start < duration_sec:
            energy_sys.tick(activity_multiplier=random.uniform(1.1, 1.8))
            t += 0.25
            
            # Draw real-time HUD
            hud = render_status_bar()
            
            # Generate waveform frame
            wave_lines = []
            for r in range(rows):
                line = ""
                y_thresh = (rows - 1 - r) / (rows - 1) * 2.0 - 1.0 # range -1.0 to 1.0
                for c in range(cols):
                    # Multi-harmonic voltage + power wave
                    val = 0.65 * math.sin(c * 0.25 + t) + 0.35 * math.sin(c * 0.1 - t * 1.5)
                    if abs(val - y_thresh) < 0.15:
                        if energy_sys.current_watts > 1200:
                            line += f"{BRIGHT_RED}⚡{RESET}"
                        elif energy_sys.current_watts > 850:
                            line += f"{BRIGHT_YELLOW}█{RESET}"
                        else:
                            line += f"{BRIGHT_GREEN}█{RESET}"
                    elif y_thresh == 0.0:
                        line += f"{GRAY}─{RESET}"
                    else:
                        line += " "
                wave_lines.append(f"  {GRAY}│{RESET}{line}{GRAY}│{RESET}")
                
            # Render frame
            output = f"\033[H\n{hud}\n\n"
            output += f"{WHITE}  [LIVE HIGH-FREQUENCY VOLTAGE & POWER WAVEFORM - 60Hz SAMPLING]{RESET}\n"
            output += f"  {DARK_GREEN}┌{'─'*cols}┐{RESET}\n"
            output += "\n".join(wave_lines) + "\n"
            output += f"  {DARK_GREEN}└{'─'*cols}┘{RESET}\n"
            output += f"  {GRAY}Telemetry: JOULES: {(energy_sys.cumulative_kwh * 3.6e6):.0f} J | CARBON: {(energy_sys.cumulative_kwh * 0.385):.3f} kg CO2e | SURGE CAP: 99.4%{RESET}\n"
            
            sys.stdout.write(output)
            sys.stdout.flush()
            time.sleep(0.08)
    except KeyboardInterrupt:
        pass
    print(f"\n{BRIGHT_GREEN}[✓] Oscilloscope monitoring paused.{RESET}\n")
    time.sleep(0.5)

def power_surge_injection():
    clear_screen()
    print(render_status_bar())
    print(f"\n{BRIGHT_RED}── [ACTION] HIGH-VOLTAGE POWER SURGE & OVERCLOCK INJECTION ──{RESET}")
    print(f"{WHITE}Injecting simulated mega-ampere pulse into quantum cyber nodes...{RESET}\n")
    
    levels = [1.5, 2.8, 4.2, 5.0, 3.5, 1.8, 1.0]
    for idx, lvl in enumerate(levels, 1):
        energy_sys.surge_level = lvl
        energy_sys.tick(activity_multiplier=lvl)
        
        w = energy_sys.current_watts
        v = energy_sys.voltage
        kwh = energy_sys.cumulative_kwh
        
        hashes = "█" * int(lvl * 5)
        spaces = "░" * (25 - len(hashes))
        
        print(f"  {GRAY}[{now_str()}]{RESET} {BRIGHT_YELLOW}PULSE #{idx:02d}:{RESET} [{BRIGHT_RED}{hashes}{GRAY}{spaces}{RESET}] -> {BRIGHT_RED}{w:6.1f} W{RESET} @ {BRIGHT_CYAN}{v:5.1f} V{RESET} | Cumulative: {BRIGHT_MAGENTA}{kwh:.4f} kWh{RESET}")
        time.sleep(0.3)
        
    energy_sys.surge_level = 0.0
    print(f"\n{BRIGHT_GREEN}[✓] Surge dissipation complete. Capacitor banks stabilized to normal threshold.{RESET}\n")
    prompt_user("Press [ENTER] to return to main console...", "")

def energy_audit_report():
    clear_screen()
    energy_sys.tick()
    print(render_status_bar())
    print(f"\n{BRIGHT_MAGENTA}── [AUDIT] CYBER_VOLT v4.2 COMPREHENSIVE ENERGY & HARDWARE TELEMETRY ──{RESET}\n")
    
    w = energy_sys.current_watts
    m_w = energy_sys.monitor_watts
    s_w = energy_sys.system_watts
    kwh = energy_sys.cumulative_kwh
    joules = kwh * 3600000.0
    cost = kwh * energy_sys.cost_rate
    carbon = kwh * 0.385 # kg CO2
    
    disp = detector.displays[0] if detector.displays else {"name": "Default", "resolution": "1080p", "refresh_rate": 60}
    
    print(f"  {BOLD}{WHITE}┌───────────────────────────────┬──────────────────────────────────────────┐{RESET}")
    print(f"  {BOLD}{WHITE}│ PARAMETER                     │ MEASURED REAL-TIME TELEMETRY             │{RESET}")
    print(f"  {BOLD}{WHITE}├───────────────────────────────┼──────────────────────────────────────────┤{RESET}")
    print(f"  │ {CYAN}Active Monitor Model{RESET}          │ {BRIGHT_YELLOW}{disp['name']:<40}{RESET} │")
    print(f"  │ {CYAN}Resolution & Refresh{RESET}          │ {BRIGHT_CYAN}{disp['resolution']} @ {disp['refresh_rate']:.1f}Hz (120Hz Fast){RESET}    │")
    print(f"  │ {CYAN}Monitor Power Consumption{RESET}     │ {BRIGHT_GREEN}{m_w:8.2f} Watts (W){RESET}                    │")
    print(f"  │ {CYAN}System/GPU Power Draw{RESET}         │ {BRIGHT_GREEN}{s_w:8.2f} Watts (Apple M4 SoC){RESET}        │")
    print(f"  │ {CYAN}Combined Real-time Power{RESET}      │ {BRIGHT_GREEN}{w:8.2f} Watts (Total Draw){RESET}          │")
    print(f"  │ {CYAN}Accumulated Energy{RESET}            │ {BRIGHT_MAGENTA}{kwh:8.5f} kWh ({joules:.0f} Joules){RESET}        │")
    print(f"  │ {CYAN}Operating Voltage (RMS){RESET}        │ {BRIGHT_CYAN}{energy_sys.voltage:8.2f} Volts (V){RESET}                  │")
    print(f"  │ {CYAN}Current Draw{RESET}                  │ {WHITE}{energy_sys.current_amps:8.2f} Amperes (A){RESET}                │")
    print(f"  │ {CYAN}System/Grid Load{RESET}              │ {render_power_bar(energy_sys.grid_load_pct, 12)}   │")
    print(f"  │ {CYAN}Core Thermal Index{RESET}            │ {BRIGHT_YELLOW}{energy_sys.core_temp_c:8.2f} °C{RESET}                         │")
    print(f"  │ {CYAN}Energy Cost Est. (USD){RESET}        │ {BRIGHT_GREEN}${cost:8.5f} USD{RESET}                       │")
    print(f"  │ {CYAN}Carbon Footprint{RESET}              │ {GRAY}{carbon:8.4f} kg CO2e{RESET}                   │")
    print(f"  {BOLD}{WHITE}└───────────────────────────────┴──────────────────────────────────────────┘{RESET}\n")
    
    prompt_user("Press [ENTER] to return to main console...", "")

def capacitor_emp_blast():
    clear_screen()
    print(render_status_bar())
    print(f"\n{BRIGHT_CYAN}── [DISCHARGE] QUANTUM CAPACITOR BANK EMP OVERLOAD BLAST ──{RESET}")
    
    print(f"{YELLOW}[*] Charging Supercapacitors to 100% capacity...{RESET}")
    for p in range(0, 101, 10):
        hashes = "█" * (p // 5)
        spaces = "░" * (20 - (p // 5))
        sys.stdout.write(f"\r  {CYAN}[{hashes}{spaces}] {p}% [VOLTAGE: {200 + p * 3} V]{RESET}")
        sys.stdout.flush()
        time.sleep(0.04)
        
    print(f"\n\n{BRIGHT_RED}💥 INITIATING ZERO-POINT EMP DISCHARGE! 💥{RESET}")
    time.sleep(0.3)
    
    for ring in range(1, 6):
        print(f"  {BRIGHT_YELLOW}⚡ »» PULSE WAVE RADIUS: {ring * 250} METERS | PEAK POWER: {random.randint(4500, 9800)} W | TRANSIENT VOLTAGE: {random.randint(1200, 4800)} V ««{RESET}")
        energy_sys.cumulative_kwh += 0.008
        time.sleep(0.12)
        
    print(f"\n{BRIGHT_GREEN}[✓] EMP cycle completed. Electromagnetic field returned to ambient background levels.{RESET}\n")
    prompt_user("Press [ENTER] to return to main console...", "")

def full_interactive_cyber_ops():
    import hacker_terminal
    # Run the interactive cyber operations suite
    clear_screen()
    print(render_status_bar())
    print(f"\n{BRIGHT_CYAN}── LAUNCHING INTEGRATED CYBER OPERATIONS ENGINE ──{RESET}\n")
    time.sleep(0.8)
    hacker_terminal.main()

def main():
    while True:
        clear_screen()
        print(render_status_bar())
        print(f"\n{BOLD}{BRIGHT_CYAN}⚡ POWER_PULSE // CYBER_VOLT v4.2 CONTROL CONSOLE ⚡{RESET}")
        print(f"{WHITE}Real-time Energy & High-Voltage Cyber Command System{RESET}")
        print(f"{DARK_GREEN}──────────────────────────────────────────────────────────────────────────────────────────────────────────────────{RESET}")
        print(f"  {BRIGHT_GREEN}[1]{RESET} {BOLD}Live Oscilloscope & Power Waveform Monitor{RESET} {GRAY}(Real-time Watts, kWh & Visual Waveform){RESET}")
        print(f"  {BRIGHT_YELLOW}[2]{RESET} {BOLD}High-Voltage Power Surge Injection{RESET} {GRAY}(Inject overdrive voltage & monitor load spikes){RESET}")
        print(f"  {BRIGHT_MAGENTA}[3]{RESET} {BOLD}Energy Consumption & Carbon Audit Report{RESET} {GRAY}(Detailed breakdown of Joules, kWh & efficiency){RESET}")
        print(f"  {BRIGHT_CYAN}[4]{RESET} {BOLD}Capacitor Bank EMP Shockwave Simulation{RESET} {GRAY}(Supercapacitor high-discharge pulse test){RESET}")
        print(f"  {BRIGHT_RED}[5]{RESET} {BOLD}Antigravity Cyber Infiltration Suite{RESET} {GRAY}(Interactive target acquisition, exploits & shell){RESET}")
        print(f"  {WHITE}[0]{RESET} {BOLD}Exit Console{RESET}")
        print(f"{DARK_GREEN}──────────────────────────────────────────────────────────────────────────────────────────────────────────────────{RESET}")
        
        choice = prompt_user("Select Option [1-5 / 0] (Default: 1):", "1")
        
        if choice == "1":
            live_oscilloscope_monitor(duration_sec=10)
        elif choice == "2":
            power_surge_injection()
        elif choice == "3":
            energy_audit_report()
        elif choice == "4":
            capacitor_emp_blast()
        elif choice == "5":
            full_interactive_cyber_ops()
        elif choice == "0" or choice.lower().startswith('q') or choice.lower().startswith('e'):
            print(f"\n{BRIGHT_GREEN}[✓] POWER_PULSE // CYBER_VOLT v4.2 gracefully offline. Final Total: {energy_sys.cumulative_kwh:.4f} kWh.{RESET}\n")
            break
        else:
            live_oscilloscope_monitor(duration_sec=6)

if __name__ == "__main__":
    main()
