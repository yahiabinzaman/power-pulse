# ⚡ CYBER_VOLT // Real-Time Power, Network Speed & Electricity Billing Cockpit

[![License: MIT](https://img.shields.io/badge/License-MIT-00ff66.svg?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-00f0ff?style=for-the-badge&logo=apple&logoColor=white)](.)
[![macOS Menu Bar Widget](https://img.shields.io/badge/macOS%20Widget-Native%20Swift-b026ff?style=for-the-badge&logo=swift&logoColor=white)](mac_widget/)
[![Python](https://img.shields.io/badge/Python-3.8%2B%20Zero--Dependency-ffb000?style=for-the-badge&logo=python&logoColor=black)](.)
[![System Architect](https://img.shields.io/badge/Architect-Yahia%20Bin%20Zaman-00ff66?style=for-the-badge&logo=github&logoColor=black)](https://github.com/yahiabinzaman)

A professional, zero-dependency, cyberpunk-themed hardware telemetry monitor and real-time electricity billing calculator for **macOS (Apple Silicon M1-M4 & Intel)** and **Windows (10/11)**. Includes a **Native macOS Menu Bar Status Widget** (`PowerPulseBar.app`) and a responsive **Web IDE Cockpit**.

---

## 🌟 Key Features

### 1. ⚡ Real-Time Hardware Power Draw Engine
- Live system wattage measurement updated every **1000ms**.
- Fine-grained power allocation across:
  - **CPU Package Workload** (Scaled to SoC TDP curves).
  - **GPU & Neural Engine Acceleration** (Photoshop, Illustrator, Metal/DirectX rendering).
  - **DRAM & SoC Motherboard Base Load**.
- Real-time Min, Average, and Peak power tracking.

### 2. 🌐 Live Internet Speed Radar & ISP Speedtest Benchmark
- **Live Download & Upload Throughput**: Real-time bandwidth monitoring in **Mbps** and **KB/s**.
- **Ping / Latency RTT**: Real-time network round-trip time in milliseconds (**ms**).
- **Session Total Network I/O**: Tracks total data transferred during the session.
- **On-Demand ISP Speedtest Benchmark**: One-click multi-stream CDN speedtest (`[SPEEDTEST]`) measuring peak connection throughput.

### 3. 💰 Electricity Cost & Tariff Projection Matrix
- Dynamic cost calculation:
  - **Hourly Rate** (e.g. `৳ 0.17 / hr`)
  - **24-Hour Cycle** (e.g. `৳ 4.08 / day`)
  - **Monthly Projection (30 Days)** (e.g. `৳ 122.42 / mo`)
- Configurable currency symbols (**৳ BDT**, **$ USD**, **€ EUR**, **₹ INR**, **£ GBP**, **AED**).
- One-click area tariff presets (e.g. **Motijheel DPDC Commercial/Office ৳10.55/unit**, **Motijheel Peak Slab ৳14.11/unit** with +5% VAT).

### 4. 🍎 Native macOS Status Bar Widget (`PowerPulseBar.app`)
- 100% native Swift application running directly in your Mac's top Menu Bar.
- Compact display: `14.8W | 1.2M` (Instant Watts & Download Speed).
- Clean interactive dropdown menu showing full hardware breakdown, ping, and electricity billing.

### 5. 🚀 Active Application Power Disassembly
- Live process table tracking active applications (Chrome, Adobe Illustrator, Photoshop, IDEs, System Compositor).
- Displays PID, Application Name, Category, CPU%, RAM (MB), Estimated Watts, Hourly Cost, and Load status (`ECO`, `MED`, `HEAVY`).

---

## 🚀 Quick Start & Installation

### 🍎 Option 1: macOS One-Click Installer & Autostart Widget
Run the installer script in terminal:
```bash
./install_mac.sh
```
- Compiles the Swift Menu Bar widget.
- Installs `PowerPulseBar.app` to `~/Applications`.
- Adds PowerPulse to **macOS Login Items** (auto-starts on boot in your Menu Bar).
- Creates a Desktop shortcut: `Launch CYBER_VOLT`.

### 🪟 Option 2: Windows One-Click Installer & Autostart
Double-click `install_windows.bat` or run:
```cmd
install_windows.bat
```
- Installs to `%LocalAppData%\PowerPulse`.
- Creates Desktop Shortcut (`CYBER_VOLT.lnk`).
- Adds to Windows Startup for auto-start on boot.

### 🌐 Option 3: Manual Launch (Web Dashboard Only)
**On macOS**:
```bash
./run_mac.sh
```

**On Windows**:
```cmd
run_windows.bat
```

Open your browser at: **`http://127.0.0.1:8765`**

---

## ⚙️ Configuration

Click the **`[CONFIG // TARIFF]`** button in the top bar to:
- Select area tariff presets (Motijheel DPDC, DESCO, or Custom).
- Enter custom per-unit electricity rates.
- Toggle +5% Bangladesh Government Electricity VAT.
- Adjust telemetry refresh rates (1.0s, 2.0s, 3.0s).

---

## 👨‍💻 Author & Credits

- **System Architect & Developer**: **Yahia Bin Zaman**
- **GitHub**: [github.com/yahiabinzaman](https://github.com/yahiabinzaman)
- **Facebook**: [facebook.com/yahiabinzaman](https://www.facebook.com/YahiaBinZaman/)
- **System**: CYBER_VOLT Core v4.2 Telemetry Engine

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
