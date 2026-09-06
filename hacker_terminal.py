import time
import random
import sys
import os
import datetime

# ==============================================================================
# INTERACTIVE CYBER OPERATIONS SUITE (AUTHORIZATION & COMMAND ENGINE)
# ==============================================================================

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

TARGETS = [
    ("104.244.42.1", "core-router-01.dc-east.internal.net", "Financial Mainframe Gateway"),
    ("198.51.100.45", "auth-gateway.corp-enterprise.com", "Active Directory SSO Server"),
    ("185.199.108.153", "edge-lb-node04.prod.cloud", "Cloud Kubernetes Cluster"),
    ("172.217.16.206", "secure-vault-backend.fin-services.org", "Encrypted Transaction DB"),
    ("192.88.99.12", "satcom-downlink.aerospace-ops.mil", "Satellite Telemetry Uplink"),
    ("203.0.113.195", "scada-plc-controller-substation-b.infra", "Power Grid SCADA Node")
]

CVE_EXPLOITS = [
    ("CVE-2024-3094", "XZ Utils liblzma Backdoor Injection", "HIGH"),
    ("CVE-2023-4863", "libwebp Heap Buffer Overflow Arbitrary RCE", "CRITICAL"),
    ("CVE-2023-38606", "Apple Kernel GMode MMIO Cache Memory Corruption", "CRITICAL"),
    ("CVE-2022-0847", "Dirty Pipe Linux Kernel Arbitrary File Overwrite", "HIGH"),
    ("CVE-2021-44228", "Apache Log4j2 JNDI Remote Code Execution", "CRITICAL")
]

ASSEMBLY_SNIPPETS = [
    ("48 89 5c 24 08", "mov    QWORD PTR [rsp+0x8], rbx"),
    ("48 89 6c 24 10", "mov    QWORD PTR [rsp+0x10], rbp"),
    ("57            ", "push   rdi"),
    ("48 83 ec 20   ", "sub    rsp, 0x20"),
    ("e8 3f 02 00 00", "call   0x7fff5a4b1040 <_sys_kernel_hook>"),
    ("85 c0         ", "test   eax, eax"),
    ("0f 05         ", "syscall (SYS_execve: /bin/sh)")
]

def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

from hardware_monitor import HardwareDetector

detector = HardwareDetector()

# Energy Tracking State
_start_time = time.time()
_cumulative_energy_kwh = 0.0025

def status_hud():
    global _cumulative_energy_kwh
    os.system('cls' if os.name == 'nt' else 'clear')
    cpu = random.randint(82, 97)
    ram = f"{random.uniform(13.1, 15.4):.1f}"
    nodes = random.randint(24, 32)
    ping = random.randint(12, 24)
    
    # Real-time power from detected hardware
    hw = detector.get_realtime_power()
    power_watts = hw["total_watts"]
    m_watts = hw["monitor_watts"]
    s_watts = hw["system_watts"]
    voltage = hw["voltage"]
    current_amps = hw["current_amps"]
    _cumulative_energy_kwh += (power_watts / 1000.0) * (random.uniform(0.5, 1.5) / 3600.0)
    grid_load = min(99.0, (power_watts / 120.0) * 100.0)
    
    disp = detector.displays[0] if detector.displays else {"name": "Monitor", "resolution": "1440p", "refresh_rate": 120.0}
    disp_str = f"{disp['name']} ({disp['resolution']} @ {disp['refresh_rate']:.0f}Hz)"
    
    # Energy status bar
    filled = int(8 * (grid_load / 100.0))
    bar = f"{BRIGHT_GREEN}{'█'*filled}{GRAY}{'░'*(8-filled)}{RESET}"
    
    print(f"{DARK_GREEN}┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐{RESET}")
    print(f"{DARK_GREEN}│ {BRIGHT_CYAN}⚡ POWER_PULSE // CYBER_VOLT v4.2{RESET} {DARK_GREEN}│{RESET} {WHITE}MONITOR:{RESET} {BRIGHT_YELLOW}{disp_str:<23}{RESET} {DARK_GREEN}│{RESET} {WHITE}GPU:{RESET} {CYAN}{detector.gpu_name:<10}{RESET} {DARK_GREEN}│{RESET} {WHITE}NODES:{RESET} {BRIGHT_CYAN}{nodes}/32{RESET} {DARK_GREEN}│{RESET}")
    print(f"{DARK_GREEN}├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤{RESET}")
    print(f"{DARK_GREEN}│ {WHITE}TOTAL POWER:{RESET} {BRIGHT_GREEN}{power_watts:5.1f}W{RESET} {GRAY}(Disp:{m_watts:.1f}W Sys:{s_watts:.1f}W){RESET} {DARK_GREEN}│{RESET} {WHITE}ENERGY:{RESET} {BRIGHT_MAGENTA}{_cumulative_energy_kwh:.4f} kWh{RESET} {DARK_GREEN}│{RESET} {WHITE}LOAD:{RESET} [{bar}] {YELLOW}{grid_load:4.1f}%{RESET} {DARK_GREEN}│{RESET}")
    print(f"{DARK_GREEN}│ {WHITE}CPU LOAD:{RESET} {RED}{cpu}%{RESET}   {DARK_GREEN}│{RESET} {WHITE}RAM:{RESET} {YELLOW}{ram}/16.0 GB{RESET}         {DARK_GREEN}│{RESET} {WHITE}LATENCY:{RESET} {GREEN}{ping}ms{RESET}            {DARK_GREEN}│{RESET} {WHITE}OPERATOR:{RESET} {BRIGHT_GREEN}ROOT_AUTHORIZED{RESET}            {DARK_GREEN}│{RESET}")
    print(f"{DARK_GREEN}└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘{RESET}")
    print(f"{GRAY}[{now_str()}] [SYSTEM] Hardware & 120Hz display power telemetry synchronized.{RESET}\n")

def prompt_user(msg, default="Y"):
    try:
        user_val = input(f"{BRIGHT_YELLOW}{msg}{RESET} ").strip()
        return user_val if user_val else default
    except (KeyboardInterrupt, EOFError):
        print(f"\n{RED}[!] Input cancelled by user.{RESET}")
        return default

def interactive_target_selection():
    print(f"{BRIGHT_CYAN}── [STAGE 0] TARGET ACQUISITION & MISSION BRIEFING ──{RESET}")
    print(f"{WHITE}Available Target Nodes in Current Geo-Cluster:{RESET}")
    for idx, (ip, host, desc) in enumerate(TARGETS, 1):
        print(f"  {BRIGHT_GREEN}[{idx}]{RESET} {WHITE}{host:<38}{RESET} {GRAY}({ip}) - {desc}{RESET}")
    
    choice = prompt_user("\n[?] Select Target ID [1-6] or press [ENTER] for Auto-Engage (Default: 1):", "1")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(TARGETS):
            target = TARGETS[idx]
        else:
            target = TARGETS[0]
    except ValueError:
        target = TARGETS[0]
        
    print(f"\n{BRIGHT_GREEN}[✓] Target Locked:{RESET} {BOLD}{target[1]} ({target[0]}) - {target[2]}{RESET}\n")
    time.sleep(0.6)
    return target

def simulate_nmap_scan(ip, hostname):
    print(f"{BRIGHT_CYAN}── [STAGE 1] NETWORK RECONNAISSANCE & PORT ENUMERATION ──{RESET}")
    print(f"{GRAY}[{now_str()}]{RESET} {WHITE}Starting Nmap 7.94 stealth SYN probe against {hostname} ({ip})...{RESET}")
    time.sleep(0.4)
    
    ports = [
        (22, "tcp", "open", "ssh", "OpenSSH 8.9p1 (Ubuntu Linux)"),
        (80, "tcp", "open", "http", "nginx/1.24.0 (Proxy Ingress)"),
        (443, "tcp", "open", "ssl/https", "Cloudflare TLS Proxy / OpenSSL 3.0.2"),
        (3306, "tcp", "open", "mysql", "MySQL Community Server 8.0.35"),
        (8443, "tcp", "open", "https-alt", "Kubernetes Ingress API Gateway v1.28"),
        (9000, "tcp", "filtered", "sonarqube", "Management Console")
    ]
    
    print(f"{BOLD}{'PORT':<10} {'STATE':<10} {'SERVICE':<15} {'VERSION'}{RESET}")
    print(f"{GRAY}--------------------------------------------------------------------------------{RESET}")
    for port, proto, state, service, ver in ports:
        state_col = f"{BRIGHT_GREEN}{state:<10}{RESET}" if state == "open" else f"{YELLOW}{state:<10}{RESET}"
        print(f"{port}/{proto:<5} {state_col} {service:<15} {GRAY}{ver}{RESET}")
        time.sleep(random.uniform(0.04, 0.08))
    print(f"{GRAY}OS Detection: Linux Kernel 5.15.0 (CPE: cpe:/o:linux:linux_kernel){RESET}\n")
    time.sleep(0.4)

def interactive_exploit_injection(ip, hostname):
    cve, name, sev = random.choice(CVE_EXPLOITS)
    print(f"{BRIGHT_YELLOW}── [STAGE 2] VULNERABILITY IDENTIFICATION & EXPLOIT SELECTION ──{RESET}")
    print(f"{GRAY}[{now_str()}]{RESET} {WHITE}Target is vulnerable to:{RESET} {BRIGHT_RED}{cve}{RESET} ({name}) - SEVERITY: {RED}{sev}{RESET}")
    print(f"{GRAY}[{now_str()}]{RESET} Available Attack Vectors:")
    print(f"  {CYAN}[1]{RESET} Automated Remote Code Execution (RCE Memory Injection)")
    print(f"  {CYAN}[2]{RESET} Privilege Escalation via Dirty Pipe (Local Rootkit)")
    print(f"  {CYAN}[3]{RESET} Reverse TCP Meterpreter Shell (Port 4444 Binding)")
    
    vector = prompt_user("\n[?] Choose Attack Vector [1/2/3] (Default: 3):", "3")
    print(f"{GRAY}[{now_str()}]{RESET} {GREEN}[✓] Vector [{vector}] Armed and Staged.{RESET}")
    
    # Permission prompt
    confirm = prompt_user(f"[CRITICAL] Authorize deployment of zero-day weapon against {ip}? [Y/n]:", "Y")
    if confirm.lower().startswith('n'):
        print(f"{RED}[!] Authorization denied by operator. Switching to passive reconnaissance...{RESET}")
        time.sleep(1)
        return
        
    print(f"{BRIGHT_GREEN}[✓] OPERATOR CLEARANCE GRANTED. INJECTING STAGE 1...{RESET}")
    time.sleep(0.4)
    
    for p in range(15, 101, 15):
        hashes = "█" * (p // 5)
        spaces = "░" * (20 - (p // 5))
        sys.stdout.write(f"\r{GRAY}[{now_str()}]{RESET} {CYAN}[{hashes}{spaces}] {p}% Payload in Ring-0 Memory... [SPEED: {random.randint(700, 950)} MB/s]{RESET}")
        sys.stdout.flush()
        time.sleep(0.05)
    print()
    print(f"{GREEN}[+]{RESET} {BRIGHT_GREEN}Meterpreter session opened! Root privilege established.{RESET}\n")
    time.sleep(0.5)

def interactive_shell_command():
    print(f"{MAGENTA}── [STAGE 3] INTERACTIVE REMOTE ROOT SHELL ──{RESET}")
    print(f"{GRAY}[{now_str()}] Interactive pseudo-terminal established (tty1).{RESET}")
    print(f"{GRAY}Type a custom bash command (e.g. 'whoami', 'cat /etc/shadow', 'ls -la', 'uname -a') or press [ENTER] to auto-execute:{RESET}")
    
    cmd = prompt_user(f"{BRIGHT_GREEN}root@{random.choice(TARGETS)[1].split('.')[0]}:~#{RESET}", "cat /etc/shadow")
    
    print(f"\n{GRAY}[{now_str()}] Executing: `{cmd}` on remote host...{RESET}")
    time.sleep(0.4)
    
    if "whoami" in cmd:
        print(f"{WHITE}root (uid=0, gid=0, groups=0(root)){RESET}")
    elif "uname" in cmd:
        print(f"{WHITE}Linux cloud-node-prod 5.15.0-89-generic #99-Ubuntu SMP x86_64 GNU/Linux{RESET}")
    elif "ls" in cmd:
        print(f"{CYAN}bin   dev  home  lib64  mnt  proc  run   srv  tmp  var\nboot  etc  lib   media  opt  root  sbin  sys  usr  .secret_vault{RESET}")
    else:
        # Shadow password dump
        print(f"{WHITE}root:$6$d9jK8$Ym2aX4b8...:19240:0:99999:7:::{RESET}")
        print(f"{WHITE}admin:$6$p2Q1a$Z0kL8w1...:19240:0:99999:7:::{RESET}")
        print(f"{WHITE}postgres:$6$v7H2p$K3nM5q9...:19240:0:99999:7:::{RESET}")
    print(f"{BRIGHT_GREEN}[✓] Command executed with return code 0 (SUCCESS).{RESET}\n")
    time.sleep(0.5)

def live_packet_sniff():
    print(f"{BRIGHT_GREEN}── [STAGE 4] LIVE PACKET SNIFFING & TLS INSPECTION ──{RESET}")
    for _ in range(6):
        src_p = random.randint(32768, 61000)
        seq = random.randint(100000, 999999)
        flags = random.choice(["[P.]", "[.]", "[S]", "[F.]"])
        ts = datetime.datetime.now().strftime("%H:%M:%S.%f")
        print(f"{GRAY}{ts}{RESET} {WHITE}IP 10.8.0.14.{src_p} > 104.244.42.1.443: Flags {flags}, seq {seq}, win 501: TLSv1.3 Application Data (Decrypted)")
        time.sleep(0.03)
    print()

def interactive_data_exfiltration():
    print(f"{BRIGHT_RED}── [STAGE 5] TARGET DATA EXTRACTION & EXFILTRATION ──{RESET}")
    print(f"{WHITE}Discovered Secret Tables in Database Cluster:{RESET}")
    print(f"  [1] `tbl_user_credentials` (14,200 rows - Passwords & API Tokens)")
    print(f"  [2] `tbl_credit_transactions` (185,900 rows - Card Numbers & CVVs)")
    print(f"  [3] `tbl_confidential_blueprints` (3.4 GB - Classified PDF/CAD files)")
    
    tbl_choice = prompt_user("\n[?] Select Database Artifact to Exfiltrate [1/2/3] (Default: 1):", "1")
    print(f"{YELLOW}[*] Encrypting and exfiltrating artifact selection [{tbl_choice}] via DNS Tunnel...{RESET}")
    
    for i in range(1, 6):
        print(f"  {GRAY}[{now_str()}]{RESET} {GREEN}Exfiltrating chunk {i}/5 -> SHA256:{''.join(random.choices('0123456789abcdef', k=32))} [DONE]{RESET}")
        time.sleep(0.06)
    print(f"{BRIGHT_GREEN}[✓] Data exfiltrated to safe encrypted proxy staging location.{RESET}\n")
    time.sleep(0.4)

def interactive_evasion_and_clean():
    print(f"{BRIGHT_YELLOW}── [STAGE 6] ANTI-FORENSIC PURGE & SHADOW CLOAKING ──{RESET}")
    clean_prompt = prompt_user("[?] Execute DoD 5220.22-M Multi-Pass Log Wipe & Sever Connection? [Y/n]:", "Y")
    
    if clean_prompt.lower().startswith('y'):
        logs = ["/var/log/auth.log", "/var/log/syslog", "/var/log/nginx/access.log", "~/.bash_history", "/var/log/wtmp"]
        for log in logs:
            print(f"{GRAY}[{now_str()}]{RESET} Wiping {WHITE}{log:<26}{RESET} -> {BRIGHT_GREEN}[OVERWRITTEN WITH 0x00]{RESET}")
            time.sleep(0.04)
        print(f"{BRIGHT_CYAN}[✓] System traces zeroed. Connection cleanly terminated.{RESET}\n")
    else:
        print(f"{YELLOW}[!] Leaving persistent backdoor listener active on port 4444.{RESET}\n")
    time.sleep(0.5)

def main():
    try:
        status_hud()
        mission_cycle = 1
        
        while True:
            print(f"{BOLD}{WHITE}══════════════════════════ [ MISSION #{mission_cycle:03d} ] ══════════════════════════{RESET}")
            
            # Step 0: User selects target
            target_ip, target_host, target_desc = interactive_target_selection()
            
            # Step 1: Recon & port scan
            simulate_nmap_scan(target_ip, target_host)
            
            # Step 2: Exploit permission & injection
            interactive_exploit_injection(target_ip, target_host)
            
            # Step 3: Interactive remote shell
            interactive_shell_command()
            
            # Step 4: Network packet sniff
            live_packet_sniff()
            
            # Step 5: Data extraction
            interactive_data_exfiltration()
            
            # Step 6: Anti-forensics purge
            interactive_evasion_and_clean()
            
            # Next cycle authorization
            next_op = prompt_user(f"{BOLD}{CYAN}[?] Mission #{mission_cycle} complete. Authorize next operation cycle? [Y/n]:{RESET}", "Y")
            if next_op.lower().startswith('n'):
                print(f"\n{GREEN}[✓] Operator session gracefully closed. Disconnected from network.{RESET}\n")
                break
                
            mission_cycle += 1
            print(f"\n{GRAY}[{now_str()}] Switching to next subnet segment...{RESET}\n")
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print(f"\n\n{BRIGHT_RED}[!] SIGINT RECEIVED -- EMERGENCY DISCONNECT!{RESET}")
        print(f"{GREEN}[✓] Active sockets closed. Safe exit.{RESET}\n")

if __name__ == "__main__":
    main()
