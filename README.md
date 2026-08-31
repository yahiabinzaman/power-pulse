# ⚡ PowerPulse — Computer Power & Electricity Cost Monitor

A modern, lightweight, cross-platform (macOS & Windows) desktop web application to monitor real-time computer power consumption (Watts), calculate electricity bills, identify power-hungry applications, and track total energy usage.

![PowerPulse Dashboard](https://raw.githubusercontent.com/user/repo/assets/dashboard.png)

---

## 🌟 Key Features

1. **⚡ Real-Time Wattage Meter**:
   - Live power draw in **Watts (W)**.
   - Separate breakdown for **CPU Package**, **GPU & Neural Engine**, and **RAM / Motherboard Base Load**.
   - Min, Average, and Peak power tracking with dynamic load status (`Idle`, `Normal`, `Heavy`).

2. **🌐 Live Internet Speed Radar & ISP Speedtest**:
   - **Live Download & Upload Throughput**: Real-time bandwidth in **Mbps** and **KB/s**.
   - **Ping / Latency RTT**: Real-time network latency in milliseconds (**ms**).
   - **Session Total Network I/O**: Total data downloaded & uploaded in **MB / GB**.
   - **On-Demand ISP Speedtest Benchmark**: One-click multi-stream CDN benchmark (`[SPEEDTEST]`) measuring peak connection speed.

3. **📈 Live Interactive Waveform Chart**:
   - Smooth 30-second live graph updated every second with Chart.js.

3. **💰 Electricity Cost & Bill Estimator**:
   - Calculates electricity costs in real-time for:
     - **Per Hour** (e.g. `৳ 0.16 / hr`)
     - **Per 24 Hours** (e.g. `৳ 3.84 / day`)
     - **Monthly Estimate (30 Days)** (e.g. `৳ 115.20 / mo`)
   - Fully customizable currency (**৳ BDT**, **$ USD**, **€ EUR**, **₹ INR**, **£ GBP**, **AED**) and unit rate (e.g. `৳ 8.50 per kWh`).

4. **🚀 Top Power-Hungry Apps & Processes**:
   - Live table listing active applications (e.g. Illustrator, Chrome, Photoshop, IDEs).
   - Shows CPU %, Memory %, Estimated Watts per application, and Energy Impact Score.

5. **🔋 Session Energy & Carbon Tracker**:
   - Total energy consumed in **kWh** during the session.
   - Total session cost and calculated CO₂ carbon footprint.

6. **💻 100% Cross-Platform & Zero Dependencies**:
   - Runs out-of-the-box using Python's standard library (no `pip install` required).
   - **macOS Engine**: Optimized for Apple Silicon (M1/M2/M3/M4) & Intel Macs.
   - **Windows Engine**: Windows WMI, Battery API & NVIDIA GPU hardware telemetry.

---

## 🚀 How to Run & Use

### 🍎 Option 1: Native macOS Status Bar Widget (Top Menu Bar)
To pin live power & internet speed directly to your Mac's top Menu Bar:
```bash
./launch_mac_widget.sh
```
- Shows live: `⚡ 14.8W  ⬇ 12.4M` in the top right of macOS.
- Click it to view full power breakdown (CPU, GPU, RAM), internet bandwidth/ping, live electricity bill, and top consuming app.
- Click **"Open Full Cyber Web Dashboard"** anytime to bring up the full UI.

### 🌐 Option 2: Full Web Dashboard IDE
**On macOS**:
```bash
./run_mac.sh
```

**On Windows**:
Double-click `run_windows.bat` or run:
```cmd
run_windows.bat
```
Open your browser at: **`http://127.0.0.1:8765`**

---

## ⚙️ Settings & Customization
Click the **[CONFIG // TARIFF]** button in the top bar to:
- Change currency symbol (`৳`, `$`, `€`, `₹`, etc.).
- Set your local electricity tariff rate (e.g., `8.50` Taka per unit).
- Adjust telemetry refresh speed (1.0s, 2.0s, 3.0s).

---

## 👨‍💻 Author & Credits
- **Architect & Developer**: **Yahia Bin Zaman**
- **System**: CYBER_VOLT Core v4.2 Telemetry Engine

