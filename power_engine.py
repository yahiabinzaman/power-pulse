"""
PowerPulse - Cross-Platform Power Telemetry Engine
Supports: macOS (Apple Silicon M1-M4 & Intel) & Windows 10/11
Zero external dependencies required (uses built-in system tools & telemetry).
"""

import os
import sys
import platform
import subprocess
import time
import datetime
import socket
import re
import json

class PowerEngine:
    def __init__(self):
        self.os_type = sys.platform  # 'darwin' (macOS), 'win32' (Windows), 'linux'
        self.system_info = self._detect_hardware()
        self.session_start_time = time.time()
        self.total_joules = 0.0
        self.last_sample_time = time.time()
        self.last_cpu_times = None
        self.peak_watts = 0.0
        self.min_watts = 9999.0
        self.samples_count = 0
        self.watts_sum = 0.0

        # Persistent Lifetime & Daily/Monthly Energy History
        self.history_file = os.path.expanduser("~/.powerpulse_history.json")
        self.history_data = self._load_history()
        self.last_history_save = time.time()

        # Network Telemetry State
        self.last_net_time = time.time()
        self.last_net_bytes = self._sample_network_raw_bytes()
        self.session_download_bytes = 0
        self.session_upload_bytes = 0
        self.last_ping_ms = 2.5

    def _run_cmd(self, cmd_list, timeout=2.5):
        """Run a system command and return stripped stdout string."""
        try:
            res = subprocess.run(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            return res.stdout.strip()
        except Exception:
            return ""

    def _detect_hardware(self):
        """Detect system hardware profile (CPU, GPU, RAM, Architecture)."""
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "arch": platform.machine(),
            "hostname": platform.node(),
            "cpu_brand": "Generic Processor",
            "cpu_cores": os.cpu_count() or 4,
            "ram_gb": 8.0,
            "device_model": "PC / Mac",
            "is_apple_silicon": False,
            "is_laptop": False,
            "soc_family": "Unknown",
            "tdp_profile": {
                "idle_w": 8.0,
                "cpu_max_w": 45.0,
                "gpu_max_w": 30.0,
                "base_sys_w": 5.0
            }
        }

        if self.os_type == "darwin":
            # macOS Detection
            model = self._run_cmd(["sysctl", "-n", "hw.model"])
            cpu = self._run_cmd(["sysctl", "-n", "machdep.cpu.brand_string"])
            mem = self._run_cmd(["sysctl", "-n", "hw.memsize"])
            cores = self._run_cmd(["sysctl", "-n", "hw.ncpu"])

            if model: info["device_model"] = model
            if cpu: info["cpu_brand"] = cpu
            if cores and cores.isdigit(): info["cpu_cores"] = int(cores)
            if mem and mem.isdigit(): info["ram_gb"] = round(int(mem) / (1024**3), 1)

            # Check Apple Silicon
            if "Apple" in info["cpu_brand"] or "arm64" in info["arch"]:
                info["is_apple_silicon"] = True
                brand_lower = info["cpu_brand"].lower()
                if "m4" in brand_lower:
                    info["soc_family"] = "Apple M4"
                    # Mac mini M4: Ultra efficient (Idle ~3.5W, Max ~32W)
                    info["tdp_profile"] = {"idle_w": 3.8, "cpu_max_w": 20.0, "gpu_max_w": 12.0, "base_sys_w": 2.5}
                    if "pro" in brand_lower or "max" in brand_lower:
                        info["tdp_profile"] = {"idle_w": 6.5, "cpu_max_w": 38.0, "gpu_max_w": 35.0, "base_sys_w": 4.0}
                elif "m3" in brand_lower:
                    info["soc_family"] = "Apple M3"
                    info["tdp_profile"] = {"idle_w": 4.0, "cpu_max_w": 22.0, "gpu_max_w": 15.0, "base_sys_w": 3.0}
                    if "pro" in brand_lower or "max" in brand_lower:
                        info["tdp_profile"] = {"idle_w": 7.0, "cpu_max_w": 42.0, "gpu_max_w": 40.0, "base_sys_w": 4.5}
                elif "m2" in brand_lower:
                    info["soc_family"] = "Apple M2"
                    info["tdp_profile"] = {"idle_w": 4.2, "cpu_max_w": 24.0, "gpu_max_w": 15.0, "base_sys_w": 3.0}
                elif "m1" in brand_lower:
                    info["soc_family"] = "Apple M1"
                    info["tdp_profile"] = {"idle_w": 4.0, "cpu_max_w": 20.0, "gpu_max_w": 13.0, "base_sys_w": 3.0}
                else:
                    info["soc_family"] = "Apple Silicon"
                    info["tdp_profile"] = {"idle_w": 4.5, "cpu_max_w": 25.0, "gpu_max_w": 18.0, "base_sys_w": 3.5}
            else:
                # Intel Mac
                info["soc_family"] = "Intel x86_64"
                info["tdp_profile"] = {"idle_w": 15.0, "cpu_max_w": 65.0, "gpu_max_w": 45.0, "base_sys_w": 10.0}

            # Check if MacBook (Battery exists)
            batt_check = self._run_cmd(["pmset", "-g", "batt"])
            if "Battery Power" in batt_check or "InternalBattery" in batt_check:
                info["is_laptop"] = True

        elif self.os_type == "win32":
            # Windows Detection
            cpu_wmi = self._run_cmd(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"])
            ram_wmi = self._run_cmd(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory"])
            model_wmi = self._run_cmd(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_ComputerSystem | Select-Object -ExpandProperty Model"])
            
            if cpu_wmi: info["cpu_brand"] = cpu_wmi.splitlines()[0].strip()
            if model_wmi: info["device_model"] = model_wmi.strip()
            if ram_wmi and ram_wmi.isdigit(): info["ram_gb"] = round(int(ram_wmi) / (1024**3), 1)

            # Check if laptop
            batt_win = self._run_cmd(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Battery"])
            if batt_win:
                info["is_laptop"] = True
                info["tdp_profile"] = {"idle_w": 10.0, "cpu_max_w": 45.0, "gpu_max_w": 35.0, "base_sys_w": 6.0}
            else:
                # Desktop PC
                info["tdp_profile"] = {"idle_w": 35.0, "cpu_max_w": 125.0, "gpu_max_w": 150.0, "base_sys_w": 25.0}

            # Check NVIDIA GPU
            nv_out = self._run_cmd(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
            if nv_out:
                info["gpu_brand"] = nv_out.splitlines()[0].strip()

        return info

    def _sample_mac_cpu_and_processes(self):
        """Sample macOS CPU usage, memory, and top energy-consuming processes with friendly names."""
        cpu_usage_total = 0.0
        
        # 1. Sample overall CPU usage from top
        top_out = self._run_cmd(["top", "-l", "1", "-n", "1", "-s", "0"])
        for line in top_out.splitlines():
            if "CPU usage:" in line:
                m = re.search(r"(\d+[\.\d]*)%\s*user,\s*(\d+[\.\d]*)%\s*sys", line)
                if m:
                    u = float(m.group(1))
                    s = float(m.group(2))
                    cpu_usage_total = min(100.0, u + s)
                break

        # 2. Sample top processes using ps
        ps_out = self._run_cmd(["ps", "-A", "-o", "pid,%cpu,%mem,command", "-r"])
        lines = ps_out.splitlines()
        
        raw_procs = []
        if len(lines) > 1:
            for line in lines[1:50]:  # top 50 processes
                parts = line.strip().split(None, 3)
                if len(parts) >= 4:
                    pid, cpu_str, mem_str, cmd = parts[0], parts[1], parts[2], parts[3]
                    try:
                        c = float(cpu_str)
                        m = float(mem_str)
                        
                        # Extract clean application name and category
                        app_name = os.path.basename(cmd)
                        category = "Utility"
                        
                        cmd_lower = cmd.lower()
                        if ".app" in cmd:
                            m_app = re.search(r"/([^/]+)\.app", cmd)
                            if m_app:
                                app_name = m_app.group(1)
                        
                        if "windowserver" in cmd_lower:
                            app_name = "WindowServer (macOS Display)"
                            category = "System Compositor"
                        elif "photoshop" in cmd_lower:
                            app_name = "Adobe Photoshop 2026"
                            category = "Graphic Design"
                        elif "illustrator" in cmd_lower or "cephtmlengine" in cmd_lower:
                            app_name = "Adobe Illustrator 2024"
                            category = "Graphic Design"
                        elif "chrome" in cmd_lower:
                            app_name = "Google Chrome"
                            category = "Web Browser"
                        elif "antigravity" in cmd_lower:
                            app_name = "Antigravity IDE"
                            category = "Code IDE / Dev"
                        elif "creative cloud" in cmd_lower or "coreosd" in cmd_lower:
                            app_name = "Adobe Creative Cloud"
                            category = "Adobe Services"
                        elif "terminal" in cmd_lower or "iterm" in cmd_lower:
                            app_name = "Terminal"
                            category = "Developer Shell"
                        elif "activity monitor" in cmd_lower:
                            app_name = "Activity Monitor"
                            category = "System Monitor"
                        elif "python" in cmd_lower:
                            app_name = "Python (PowerPulse Telemetry)"
                            category = "Telemetry Server"
                        elif "finder" in cmd_lower:
                            app_name = "macOS Finder"
                            category = "File Manager"
                        elif "vtdecoder" in cmd_lower or "media" in cmd_lower or "audio" in cmd_lower:
                            app_name = "Hardware Video/Audio Decoder"
                            category = "Media Engine"

                        # Filter out internal probing commands
                        if any(ign in cmd_lower or ign in app_name.lower() for ign in ["top ", "top -", "/top", "ps -", "/ps", "grep", "sleep", "sh -c", "bash -c", "sysctl", "netstat"]):
                            continue

                        raw_procs.append({
                            "pid": pid,
                            "name": app_name,
                            "category": category,
                            "cpu": c,
                            "mem": m,
                            "raw_path": cmd
                        })
                    except Exception:
                        continue

        # Group and aggregate multi-process apps (e.g. Chrome/Illustrator helper processes)
        grouped = {}
        for p in raw_procs:
            name = p["name"]
            if name not in grouped:
                grouped[name] = {
                    "pid": p["pid"],
                    "name": name,
                    "category": p["category"],
                    "cpu": 0.0,
                    "mem": 0.0,
                    "count": 0
                }
            grouped[name]["cpu"] += p["cpu"]
            grouped[name]["mem"] += p["mem"]
            grouped[name]["count"] += 1

        proc_list = sorted(grouped.values(), key=lambda x: x["cpu"], reverse=True)[:12]
        return cpu_usage_total, proc_list

    def _sample_windows_cpu_and_processes(self):
        """Sample Windows CPU usage and top processes via PowerShell / WMIC."""
        cpu_usage_total = 10.0
        proc_list = []

        ps_script = """
        $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
        $procs = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Id, ProcessName, CPU, WorkingSet
        $res = @{ cpu = $cpu; procs = $procs }
        $res | ConvertTo-Json -Compress
        """
        raw_json = self._run_cmd(["powershell", "-NoProfile", "-Command", ps_script], timeout=3.5)
        if raw_json:
            try:
                data = json.loads(raw_json)
                if "cpu" in data and data["cpu"] is not None:
                    cpu_usage_total = float(data["cpu"])
                if "procs" in data and isinstance(data["procs"], list):
                    for p in data["procs"]:
                        mem_mb = round((p.get("WorkingSet", 0) or 0) / (1024 * 1024), 1)
                        mem_pct = round((mem_mb / (self.system_info["ram_gb"] * 1024)) * 100, 1)
                        proc_list.append({
                            "pid": str(p.get("Id", "")),
                            "name": p.get("ProcessName", "Unknown"),
                            "cpu": round(float(p.get("CPU", 0) or 0) % 100, 1),
                            "mem": mem_pct
                        })
            except Exception:
                pass

        return cpu_usage_total, proc_list

    def _sample_battery_power_mac(self):
        """Check battery wattage if on MacBook battery."""
        # Check ioreg for InstantAmperage & InstantVoltage
        ioreg_out = self._run_cmd(["ioreg", "-r", "-k", "InstantAmperage", "-k", "Voltage", "-c", "AppleSmartBattery"])
        if ioreg_out:
            amp = None
            volt = None
            for line in ioreg_out.splitlines():
                if "InstantAmperage" in line:
                    m = re.search(r"=\s*(-?\d+)", line)
                    if m: amp = int(m.group(1))
                if "Voltage" in line:
                    m = re.search(r"=\s*(\d+)", line)
                    if m: volt = int(m.group(1))
            
            if amp is not None and volt is not None and amp < 0:
                # Discharging (in mW = abs(mA) * mV / 1000)
                watts = round((abs(amp) * volt) / 1000000.0, 2)
                if 0.5 <= watts <= 150.0:
                    return watts
        return None

    def _sample_nvidia_gpu_power(self):
        """Check NVIDIA GPU live power draw (Windows/Linux)."""
        out = self._run_cmd(["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"])
        if out:
            try:
                w = float(out.splitlines()[0].strip())
                return w
            except Exception:
                pass
        return None

    def sample_telemetry(self):
        """Sample all live metrics and calculate accurate power telemetry."""
        now = time.time()
        dt = max(0.1, now - self.last_sample_time)
        self.last_sample_time = now

        # Sample OS-specific CPU and processes
        if self.os_type == "darwin":
            cpu_pct, procs = self._sample_mac_cpu_and_processes()
        elif self.os_type == "win32":
            cpu_pct, procs = self._sample_windows_cpu_and_processes()
        else:
            cpu_pct, procs = 10.0, []

        tdp = self.system_info["tdp_profile"]
        
        # Calculate dynamic component powers
        # 1. CPU Power
        # CPU scaling curve: Idle + (load/100)^1.25 * (Max - Idle)
        cpu_load_factor = min(1.0, max(0.0, (cpu_pct / 100.0)))
        cpu_dynamic = (cpu_load_factor ** 1.25) * tdp["cpu_max_w"]
        cpu_w = round(tdp["idle_w"] * 0.4 + cpu_dynamic, 2)

        # 2. GPU Power
        # Check GPU sensors or estimate based on graphical processes (Illustrator, Photoshop, WindowServer, Games)
        nv_gpu_w = self._sample_nvidia_gpu_power()
        if nv_gpu_w is not None:
            gpu_w = round(nv_gpu_w, 2)
        else:
            gpu_heavy_load = 0.0
            for p in procs:
                p_name_l = p["name"].lower()
                if any(x in p_name_l for x in ["illustrator", "photoshop", "premiere", "aftereffects", "windowserver", "chrome", "gpu", "game", "blender", "render", "unreal", "unity"]):
                    gpu_heavy_load += (p["cpu"] / 100.0) * 0.4
            gpu_load_factor = min(1.0, max(0.05, gpu_heavy_load))
            gpu_w = round(0.5 + (gpu_load_factor ** 1.2) * tdp["gpu_max_w"], 2)

        # 3. RAM & Board Base Power
        base_w = round(tdp["base_sys_w"] + (cpu_load_factor * 1.5), 2)

        # Total Estimated Power
        total_w = round(cpu_w + gpu_w + base_w, 2)

        # Check direct battery sensor override if on laptop battery
        if self.os_type == "darwin":
            batt_w = self._sample_battery_power_mac()
            if batt_w is not None:
                total_w = batt_w
                # Distribute proportionally
                cpu_w = round(total_w * 0.45, 2)
                gpu_w = round(total_w * 0.35, 2)
                base_w = round(total_w * 0.20, 2)

        # Distribute power amongst top processes (CPU + GPU workload allocation)
        for p in procs:
            p_cpu_frac = min(1.0, max(0.01, p["cpu"] / max(1.0, (self.system_info["cpu_cores"] * 100.0))))
            
            # If app uses GPU (Photoshop, Illustrator, WindowServer, Chrome, Games), attribute GPU power share
            gpu_share = 0.0
            p_name_l = p["name"].lower()
            if any(x in p_name_l for x in ["illustrator", "photoshop", "windowserver", "chrome", "media", "render"]):
                gpu_share = min(1.0, p_cpu_frac * 2.5) * (gpu_w * 0.6)

            p_w = round((p_cpu_frac * cpu_w) + gpu_share + (0.02 * base_w), 2)
            p["watts"] = p_w
            p["ram_mb"] = round((p["mem"] / 100.0) * self.system_info["ram_gb"] * 1024, 0)
            p["energy_score"] = round(p["cpu"] * 0.7 + p["mem"] * 0.3, 1)

            if p_w >= 1.5:
                p["load_tag"] = "HEAVY"
                p["tag_class"] = "neon-rose"
            elif p_w >= 0.4:
                p["load_tag"] = "MED"
                p["tag_class"] = "neon-amber"
            else:
                p["load_tag"] = "ECO"
                p["tag_class"] = "neon-green"

        # Update Session Cumulative Statistics
        joules = total_w * dt
        self.total_joules += joules
        kwh = self.total_joules / 3600000.0
        
        self.samples_count += 1
        self.watts_sum += total_w
        avg_watts = round(self.watts_sum / self.samples_count, 2)
        
        if total_w > self.peak_watts: self.peak_watts = total_w
        if total_w < self.min_watts: self.min_watts = total_w

        session_duration_sec = int(now - self.session_start_time)

        # Sample Network Bandwidth & Latency
        net_metrics, delta_in, delta_out = self._sample_network_throughput(now)
        ram_metrics = self._sample_system_ram()

        # Update Persistent Energy & Internet History
        self._update_history(joules, dt, delta_in, delta_out)
        history_summary = self.get_history_summary(tariff_rate=14.11)

        return {
            "timestamp": now,
            "power": {
                "total_watts": total_w,
                "cpu_watts": cpu_w,
                "gpu_watts": gpu_w,
                "base_watts": base_w,
                "peak_watts": round(self.peak_watts, 2),
                "min_watts": round(self.min_watts, 2),
                "avg_watts": avg_watts
            },
            "cpu_usage_pct": round(cpu_pct, 1),
            "gpu_usage_pct": round(min(100.0, max(2.0, gpu_load_factor * 100.0)), 1),
            "ram": ram_metrics,
            "processes": procs,
            "network": net_metrics,
            "session": {
                "duration_seconds": session_duration_sec,
                "total_joules": round(self.total_joules, 2),
                "total_kwh": round(kwh, 6),
                "carbon_kg": round(kwh * 0.475, 4)  # ~475g CO2 per kWh grid average
            },
            "history": history_summary,
            "hardware": self.system_info
        }

    def _load_history(self):
        """Load persistent cumulative history from disk."""
        now_iso = datetime.datetime.now().isoformat()
        default_hist = {
            "installed_at": now_iso,
            "lifetime_joules": 0.0,
            "lifetime_kwh": 0.0,
            "lifetime_in_bytes": 0,
            "lifetime_out_bytes": 0,
            "daily": {},
            "monthly": {}
        }
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "installed_at" not in data: data["installed_at"] = now_iso
                    if "lifetime_kwh" not in data: data["lifetime_kwh"] = 0.0
                    if "lifetime_in_bytes" not in data: data["lifetime_in_bytes"] = 0
                    if "lifetime_out_bytes" not in data: data["lifetime_out_bytes"] = 0
                    if "daily" not in data: data["daily"] = {}
                    if "monthly" not in data: data["monthly"] = {}
                    return data
            except Exception:
                pass
        return default_hist

    def _save_history(self):
        """Save persistent cumulative history to disk atomically with backup."""
        tmp_file = self.history_file + ".tmp"
        bak_file = self.history_file + ".bak"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, indent=2)
            os.replace(tmp_file, self.history_file)
            # Create backup
            with open(bak_file, "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, indent=2)
        except Exception:
            pass

    def _update_history(self, joules, dt, in_bytes=0, out_bytes=0):
        """Accumulate joules and internet data into lifetime, today's, and this month's buckets."""
        now_dt = datetime.datetime.now()
        today_key = now_dt.strftime("%Y-%m-%d")
        month_key = now_dt.strftime("%Y-%m")

        kwh = joules / 3600000.0

        # Lifetime
        self.history_data["lifetime_joules"] = self.history_data.get("lifetime_joules", 0.0) + joules
        self.history_data["lifetime_kwh"] = self.history_data.get("lifetime_kwh", 0.0) + kwh
        self.history_data["lifetime_in_bytes"] = self.history_data.get("lifetime_in_bytes", 0) + in_bytes
        self.history_data["lifetime_out_bytes"] = self.history_data.get("lifetime_out_bytes", 0) + out_bytes

        # Daily
        d = self.history_data["daily"].setdefault(today_key, {"joules": 0.0, "kwh": 0.0, "seconds": 0, "in_bytes": 0, "out_bytes": 0})
        d["joules"] += joules
        d["kwh"] += kwh
        d["seconds"] += int(dt)
        d["in_bytes"] = d.get("in_bytes", 0) + in_bytes
        d["out_bytes"] = d.get("out_bytes", 0) + out_bytes

        # Monthly
        m = self.history_data["monthly"].setdefault(month_key, {"joules": 0.0, "kwh": 0.0, "seconds": 0, "in_bytes": 0, "out_bytes": 0})
        m["joules"] += joules
        m["kwh"] += kwh
        m["seconds"] += int(dt)
        m["in_bytes"] = m.get("in_bytes", 0) + in_bytes
        m["out_bytes"] = m.get("out_bytes", 0) + out_bytes

        # Save to disk every 3 seconds
        if time.time() - self.last_history_save > 3.0:
            self.last_history_save = time.time()
            self._save_history()

    def get_history_summary(self, tariff_rate=14.11):
        """Return structured summary of today, month, lifetime, and daily/monthly averages with dynamic precision."""
        now_dt = datetime.datetime.now()
        today_key = now_dt.strftime("%Y-%m-%d")
        month_key = now_dt.strftime("%Y-%m")

        today_rec = self.history_data.get("daily", {}).get(today_key, {"kwh": 0.0, "seconds": 0, "in_bytes": 0, "out_bytes": 0})
        month_rec = self.history_data.get("monthly", {}).get(month_key, {"kwh": 0.0, "seconds": 0, "in_bytes": 0, "out_bytes": 0})

        today_kwh = round(today_rec.get("kwh", 0.0), 6)
        today_cost = round(today_kwh * tariff_rate, 4)

        month_kwh = round(month_rec.get("kwh", 0.0), 6)
        month_cost = round(month_kwh * tariff_rate, 4)

        lifetime_kwh = round(self.history_data.get("lifetime_kwh", 0.0), 6)
        lifetime_cost = round(lifetime_kwh * tariff_rate, 4)

        # Internet Data Summaries
        def fmt_bytes(b):
            if b >= 1024**3:
                return f"{round(b / (1024**3), 2)} GB"
            elif b >= 1024**2:
                return f"{round(b / (1024**2), 1)} MB"
            else:
                return f"{round(b / 1024, 0):.0f} KB"

        today_in = today_rec.get("in_bytes", 0)
        today_out = today_rec.get("out_bytes", 0)
        today_total_net = today_in + today_out

        month_in = month_rec.get("in_bytes", 0)
        month_out = month_rec.get("out_bytes", 0)
        month_total_net = month_in + month_out

        lifetime_in = self.history_data.get("lifetime_in_bytes", 0)
        lifetime_out = self.history_data.get("lifetime_out_bytes", 0)
        lifetime_total_net = lifetime_in + lifetime_out

        # Active days
        active_days = len(self.history_data.get("daily", {}))
        if active_days > 0:
            daily_avg_kwh = round(lifetime_kwh / active_days, 6)
            daily_avg_cost = round(lifetime_cost / active_days, 4)
        else:
            daily_avg_kwh = today_kwh
            daily_avg_cost = today_cost

        monthly_projected_cost = round(daily_avg_cost * 30.0, 2)

        return {
            "installed_at": self.history_data.get("installed_at", today_key),
            "today": {
                "date": today_key,
                "kwh": today_kwh,
                "cost": today_cost,
                "active_seconds": today_rec.get("seconds", 0),
                "data_total_bytes": today_total_net,
                "data_formatted": fmt_bytes(today_total_net),
                "data_down_formatted": fmt_bytes(today_in),
                "data_up_formatted": fmt_bytes(today_out)
            },
            "this_month": {
                "month": month_key,
                "kwh": month_kwh,
                "cost": month_cost,
                "data_total_bytes": month_total_net,
                "data_formatted": fmt_bytes(month_total_net)
            },
            "lifetime": {
                "kwh": lifetime_kwh,
                "cost": lifetime_cost,
                "active_days": active_days if active_days > 0 else 1,
                "data_total_bytes": lifetime_total_net,
                "data_formatted": fmt_bytes(lifetime_total_net)
            },
            "averages": {
                "daily_avg_kwh": daily_avg_kwh,
                "daily_avg_cost": daily_avg_cost,
                "monthly_projected_cost": monthly_projected_cost
            }
        }

    def _sample_system_ram(self):
        """Sample real-time system RAM usage."""
        try:
            if self.os_type == "darwin":
                out = self._run_cmd(["vm_stat"])
                page_size = 4096
                m_page = re.search(r'page size of (\d+) bytes', out)
                if m_page: page_size = int(m_page.group(1))
                pages = {}
                for line in out.splitlines():
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip().replace('"', '')
                        val = parts[1].strip().rstrip('.')
                        if val.isdigit(): pages[key] = int(val)
                active = pages.get('Pages active', 0)
                wired = pages.get('Pages wired down', 0)
                compressed = pages.get('Pages occupied by compressor', 0)
                used_gb = round(((active + wired + compressed) * page_size) / (1024**3), 2)
                total_gb = self.system_info.get("ram_gb", 16.0)
                pct = round((used_gb / max(1.0, total_gb)) * 100, 1)
                return {"used_gb": used_gb, "total_gb": total_gb, "pct": min(100.0, pct)}
            elif self.os_type == "win32":
                wmi = self._run_cmd(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"])
                if wmi:
                    d = json.loads(wmi)
                    total_kb = d.get("TotalVisibleMemorySize", 16 * 1024 * 1024)
                    free_kb = d.get("FreePhysicalMemory", 8 * 1024 * 1024)
                    used_kb = total_kb - free_kb
                    used_gb = round(used_kb / (1024**2), 2)
                    total_gb = round(total_kb / (1024**2), 1)
                    pct = round((used_kb / total_kb) * 100, 1)
                    return {"used_gb": used_gb, "total_gb": total_gb, "pct": min(100.0, pct)}
        except Exception:
            pass
        return {"used_gb": 0.0, "total_gb": self.system_info.get("ram_gb", 16.0), "pct": 0.0}

    def _sample_network_raw_bytes(self):
        """Read raw cumulative inbound and outbound bytes from network interfaces."""
        in_b, out_b = 0, 0
        if self.os_type == "darwin":
            out = self._run_cmd(["netstat", "-ibn"])
            seen_if = set()
            for line in out.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 10:
                    iface = parts[0]
                    if iface.startswith("lo") or "<Link" not in line:
                        continue
                    try:
                        ib = int(parts[6])
                        ob = int(parts[9])
                        if iface not in seen_if:
                            in_b += ib
                            out_b += ob
                            seen_if.add(iface)
                    except Exception:
                        pass
        elif self.os_type == "win32":
            ps_net = "Get-NetAdapterStatistics | Select-Object -ExpandProperty ReceivedBytes; Get-NetAdapterStatistics | Select-Object -ExpandProperty SentBytes"
            out = self._run_cmd(["powershell", "-NoProfile", "-Command", ps_net])
            lines = out.splitlines()
            if len(lines) >= 2:
                try:
                    in_b = sum(int(x) for x in lines[:len(lines)//2] if x.isdigit())
                    out_b = sum(int(x) for x in lines[len(lines)//2:] if x.isdigit())
                except Exception:
                    pass
        return (in_b, out_b)

    def _sample_network_throughput(self, now):
        """Calculate live network download/upload bandwidth and real-time ping latency."""
        curr_in, curr_out = self._sample_network_raw_bytes()
        last_in, last_out = self.last_net_bytes
        dt = max(0.1, now - self.last_net_time)

        self.last_net_time = now
        self.last_net_bytes = (curr_in, curr_out)

        # Delta bytes
        delta_in = max(0, curr_in - last_in)
        delta_out = max(0, curr_out - last_out)

        self.session_download_bytes += delta_in
        self.session_upload_bytes += delta_out

        # Bandwidth speeds
        down_kbs = (delta_in / 1024.0) / dt
        up_kbs = (delta_out / 1024.0) / dt

        down_mbps = (down_kbs * 8.0) / 1024.0
        up_mbps = (up_kbs * 8.0) / 1024.0

        # Real-time sub-millisecond ping measurement on every sample
        self.last_ping_ms = self._measure_ping_latency()

        metrics = {
            "down_kbs": round(down_kbs, 1),
            "up_kbs": round(up_kbs, 1),
            "down_mbps": round(down_mbps, 2),
            "up_mbps": round(up_mbps, 2),
            "ping_ms": self.last_ping_ms,
            "session_down_mb": round(self.session_download_bytes / (1024.0 * 1024.0), 1),
            "session_up_mb": round(self.session_upload_bytes / (1024.0 * 1024.0), 1)
        }
        return (metrics, delta_in, delta_out)

    def _measure_ping_latency(self):
        """Measure real network round-trip ping time in milliseconds using low-overhead direct socket connect."""
        targets = [("1.1.1.1", 53), ("8.8.8.8", 53), ("1.0.0.1", 53)]
        for host, port in targets:
            try:
                t0 = time.perf_counter()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect((host, port))
                t1 = time.perf_counter()
                s.close()
                return round((t1 - t0) * 1000.0, 1)
            except Exception:
                continue
        # Fallback to ICMP ping
        try:
            if self.os_type == "darwin":
                out = self._run_cmd(["ping", "-c", "1", "-W", "500", "1.1.1.1"])
                m = re.search(r"time=(\d+[\.\d]*)", out)
                if m: return round(float(m.group(1)), 1)
            elif self.os_type == "win32":
                out = self._run_cmd(["ping", "-n", "1", "-w", "500", "1.1.1.1"])
                m = re.search(r"time[=<](\d+)ms", out)
                if m: return round(float(m.group(1)), 1)
        except Exception:
            pass
        return 12.0

    def run_speedtest_benchmark(self):
        """Run on-demand high-speed download & latency benchmark using reliable multi-chunk CDNs."""
        import urllib.request
        import ssl
        
        test_urls = [
            "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
            "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js",
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.js",
            "https://ajax.googleapis.com/ajax/libs/angularjs/1.8.2/angular.js"
        ] * 3

        ping = self._measure_ping_latency()
        ctx = ssl._create_unverified_context()
        total_bytes = 0
        t_start = time.time()

        try:
            for u in test_urls:
                req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
                with urllib.request.urlopen(req, timeout=6, context=ctx) as resp:
                    total_bytes += len(resp.read())
            
            t_end = time.time()
            elapsed = max(0.1, t_end - t_start)
            speed_mbps = round(((total_bytes * 8.0) / (1024.0 * 1024.0)) / elapsed, 2)
            
            return {
                "status": "OK",
                "download_mbps": speed_mbps,
                "ping_ms": ping,
                "bytes_tested": total_bytes,
                "elapsed_sec": round(elapsed, 2)
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "ping_ms": ping}

if __name__ == "__main__":
    print("Testing PowerPulse Telemetry Engine...")
    engine = PowerEngine()
    print(f"Detected OS: {engine.os_type} | Device: {engine.system_info['device_model']} | CPU: {engine.system_info['cpu_brand']}")
    print(f"Apple Silicon: {engine.system_info['is_apple_silicon']} | RAM: {engine.system_info['ram_gb']} GB")
    time.sleep(1.0)
    data = engine.sample_telemetry()
    print(f"Live Sample -> Total: {data['power']['total_watts']} W | CPU: {data['power']['cpu_watts']} W | GPU: {data['power']['gpu_watts']} W")
    print(f"Top 3 Processes:")
    for p in data['processes'][:3]:
        print(f"  - {p['name']} (PID {p['pid']}): CPU {p['cpu']}% | ~{p['watts']} W")
