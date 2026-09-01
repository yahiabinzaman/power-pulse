# ==============================================================================
# POWER_PULSE // Native Windows Live System Tray & Floating HUD Widget
# Developed for Yahia Bin Zaman
# ==============================================================================
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Web

[System.Windows.Forms.Application]::EnableVisualStyles()

# Global State
$script:Port = 8765
$script:ApiUrl = "http://127.0.0.1:$script:Port/api/telemetry"
$script:TariffRate = 25.00
$script:Currency = [char]0x09F3 # ৳ Bengali Taka symbol

# Auto-spawn backend daemon if not running
function Ensure-ServerRunning {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect("127.0.0.1", $script:Port, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne(400, $false)
        if ($wait) {
            $tcp.EndConnect($iar)
            $tcp.Close()
            return
        }
    } catch {}

    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $appPy = Join-Path (Split-Path -Parent $scriptDir) "app.py"
    if (Test-Path $appPy) {
        $pyExe = $null
        foreach ($name in @("pythonw.exe", "pyw.exe", "python.exe", "py.exe")) {
            $cmd = Get-Command $name -ErrorAction SilentlyContinue
            if ($null -ne $cmd) { $pyExe = $cmd.Source; break }
        }
        if ($null -eq $pyExe) {
            $candidates = @(
                "$env:LocalAppData\Programs\Python\Python313\pythonw.exe",
                "$env:LocalAppData\Programs\Python\Python312\pythonw.exe",
                "$env:LocalAppData\Programs\Python\Python311\pythonw.exe",
                "$env:LocalAppData\Programs\Python\Python310\pythonw.exe",
                "C:\Python313\pythonw.exe",
                "C:\Python312\pythonw.exe",
                "C:\Python311\pythonw.exe"
            )
            foreach ($c in $candidates) {
                if (Test-Path $c) { $pyExe = $c; break }
            }
        }
        if ($null -eq $pyExe) { $pyExe = "pythonw.exe" }
        Start-Process -FilePath $pyExe -ArgumentList "`"$appPy`"" -WindowStyle Hidden -ErrorAction SilentlyContinue
    }
}

# Create System Tray NotifyIcon
$script:notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$script:notifyIcon.Text = "PowerPulse // Initializing..."
$script:notifyIcon.Visible = $true

# Draw dynamic custom 16x16 / 32x32 tray icon
function New-TrayIcon([string]$text) {
    $bmp = New-Object System.Drawing.Bitmap 32, 32
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias

    # Background Squircle
    $rect = New-Object System.Drawing.Rectangle 1, 1, 30, 30
    $brushBg = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 10, 14, 20))
    $g.FillEllipse($brushBg, $rect)

    # Neon rim
    $pen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(255, 0, 255, 102)), 2
    $g.DrawEllipse($pen, $rect)

    # Center pulse bolt
    $brushText = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 0, 240, 255))
    $font = New-Object System.Drawing.Font "Segoe UI", 12, [System.Drawing.FontStyle]::Bold
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment = [System.Drawing.StringAlignment]::Center
    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center
    $g.DrawString($text, $font, $brushText, (New-Object System.Drawing.RectangleF 0, 0, 32, 32), $sf)

    $hIcon = $bmp.GetHicon()
    return [System.Drawing.Icon]::FromHandle($hIcon)
}

$script:notifyIcon.Icon = New-TrayIcon "P"

# Context Menu
$script:contextMenu = New-Object System.Windows.Forms.ContextMenuStrip
$script:notifyIcon.ContextMenuStrip = $script:contextMenu

# Meter Bar Helper
function Make-Meter([double]$pct, [int]$len = 8) {
    $clamped = [Math]::Max(0.0, [Math]::Min(100.0, $pct))
    $filled = [int][Math]::Round(($clamped / 100.0) * $len)
    $empty = [Math]::Max(0, $len - $filled)
    return "[" + ("■" * $filled) + ("·" * $empty) + "]"
}

# Update Context Menu with Live Activities
function Update-MenuUI($data) {
    $script:contextMenu.Items.Clear()

    # Header
    $h = $script:contextMenu.Items.Add("POWER_PULSE // LIVE TELEMETRY")
    $h.Font = New-Object System.Drawing.Font "Segoe UI", 9, [System.Drawing.FontStyle]::Bold
    $h.Enabled = $false
    $script:contextMenu.Items.Add("-") | Out-Null

    if ($null -ne $data) {
        $p = $data.power
        $cpu = $data.cpu_usage_pct
        $gpu = if ($null -ne $data.gpu_usage_pct) { $data.gpu_usage_pct } else { 8.0 }
        $ram = $data.ram
        $net = $data.network
        $hist = $data.history

        # 1. System Resource Activities
        $rHeader = $script:contextMenu.Items.Add("System Resource Activities")
        $rHeader.Font = New-Object System.Drawing.Font "Segoe UI", 9, [System.Drawing.FontStyle]::Bold
        $rHeader.Enabled = $false

        $cpuMeter = Make-Meter $cpu
        $script:contextMenu.Items.Add("  CPU Load:  $cpuMeter  $([Math]::Round($cpu, 1))% ($([Math]::Round($p.cpu_watts, 1)) W)") | Out-Null

        $gpuMeter = Make-Meter $gpu
        $script:contextMenu.Items.Add("  GPU Load:  $gpuMeter  $([Math]::Round($gpu, 1))% ($([Math]::Round($p.gpu_watts, 1)) W)") | Out-Null

        if ($null -ne $ram) {
            $ramMeter = Make-Meter $ram.pct
            $script:contextMenu.Items.Add("  RAM Usage: $ramMeter  $([Math]::Round($ram.pct, 1))% ($([Math]::Round($ram.used_gb, 1)) GB / $([Math]::Round($ram.total_gb, 1)) GB)") | Out-Null
        }
        $script:contextMenu.Items.Add("-") | Out-Null

        # 2. Power Telemetry
        $pHeader = $script:contextMenu.Items.Add("Total Power Draw: $([Math]::Round($p.total_watts, 2)) Watts")
        $pHeader.Font = New-Object System.Drawing.Font "Segoe UI", 9, [System.Drawing.FontStyle]::Bold
        $pHeader.Enabled = $false

        $script:contextMenu.Items.Add("  CPU Package:      $([Math]::Round($p.cpu_watts, 1)) W") | Out-Null
        $script:contextMenu.Items.Add("  GPU Dedicated:    $([Math]::Round($p.gpu_watts, 1)) W") | Out-Null
        $script:contextMenu.Items.Add("  Base / Motherboard: $([Math]::Round($p.base_watts, 1)) W") | Out-Null
        $script:contextMenu.Items.Add("  Min: $([Math]::Round($p.min_watts, 1))W | Avg: $([Math]::Round($p.avg_watts, 1))W | Peak: $([Math]::Round($p.peak_watts, 1))W") | Out-Null
        $script:contextMenu.Items.Add("-") | Out-Null

        # 3. Active Applications
        if ($null -ne $data.processes -and $data.processes.Count -gt 0) {
            $aHeader = $script:contextMenu.Items.Add("Active Applications (Power Draw)")
            $aHeader.Font = New-Object System.Drawing.Font "Segoe UI", 9, [System.Drawing.FontStyle]::Bold
            $aHeader.Enabled = $false

            $idx = 1
            foreach ($proc in $data.processes | Select-Object -First 4) {
                $w = [Math]::Round($proc.watts, 2)
                $tag = if ($w -gt 2.0) { "[HEAVY]" } elseif ($w -gt 0.5) { "[MED]" } else { "[ECO]" }
                $script:contextMenu.Items.Add("  $idx. $($proc.name): $w W (CPU $([Math]::Round($proc.cpu, 1))%) $tag") | Out-Null
                $idx++
            }
            $script:contextMenu.Items.Add("-") | Out-Null
        }

        # 4. Network Telemetry & Daily Data Usage
        if ($null -ne $net) {
            $nHeader = $script:contextMenu.Items.Add("Network Telemetry")
            $nHeader.Font = New-Object System.Drawing.Font "Segoe UI", 9, [System.Drawing.FontStyle]::Bold
            $nHeader.Enabled = $false

            $script:contextMenu.Items.Add("  Download: $([Math]::Round($net.down_mbps, 2)) Mbps ($([Math]::Round($net.down_kbs, 1)) KB/s)") | Out-Null
            $script:contextMenu.Items.Add("  Upload:   $([Math]::Round($net.up_mbps, 2)) Mbps ($([Math]::Round($net.up_kbs, 1)) KB/s)") | Out-Null

            if ($null -ne $hist.today.data_formatted) {
                $script:contextMenu.Items.Add("  Today's Data:   $($hist.today.data_formatted) (Down: $($hist.today.data_down_formatted) | Up: $($hist.today.data_up_formatted))") | Out-Null
            }
            if ($null -ne $hist.this_month.data_formatted) {
                $script:contextMenu.Items.Add("  This Month:     $($hist.this_month.data_formatted)") | Out-Null
            }
            $script:contextMenu.Items.Add("  Latency:  $([Math]::Round($net.ping_ms, 1)) ms (Ping)") | Out-Null
            $script:contextMenu.Items.Add("-") | Out-Null
        }

        # 5. Electricity Cost & Energy Tracking
        $cHeader = $script:contextMenu.Items.Add("Electricity Cost & Energy (@ $script:Currency 25.00/kWh)")
        $cHeader.Font = New-Object System.Drawing.Font "Segoe UI", 9, [System.Drawing.FontStyle]::Bold
        $cHeader.Enabled = $false

        $costHr = ($p.total_watts / 1000.0) * $script:TariffRate
        $script:contextMenu.Items.Add("  Live Rate:        $script:Currency $([Math]::Round($costHr, 3)) / hr ($([Math]::Round($p.total_watts, 1)) W)") | Out-Null

        if ($null -ne $hist) {
            function Format-Cost($c, $k) {
                if ($c -ge 1.0) { return "$script:Currency $([Math]::Round($c, 2)) ($([Math]::Round($k, 3)) kWh)" }
                elseif ($c -gt 0.00001) { return "$script:Currency $([Math]::Round($c, 3)) ($([Math]::Round($k, 4)) kWh)" }
                else { return "$script:Currency 0.00 (0.000 kWh)" }
            }
            $script:contextMenu.Items.Add("  Today's Bill:     $(Format-Cost $hist.today.cost $hist.today.kwh)") | Out-Null
            $script:contextMenu.Items.Add("  This Month:       $(Format-Cost $hist.this_month.cost $hist.this_month.kwh)") | Out-Null
            $script:contextMenu.Items.Add("  All-Time Total:   $(Format-Cost $hist.lifetime.cost $hist.lifetime.kwh)") | Out-Null
            $script:contextMenu.Items.Add("  Daily Average:    $script:Currency $([Math]::Round($hist.averages.daily_avg_cost, 2)) / day") | Out-Null
            $script:contextMenu.Items.Add("  Monthly Estimate: $script:Currency $([Math]::Round($hist.averages.monthly_projected_cost, 2)) (30d Projection)") | Out-Null

            $installDate = if ($null -ne $hist.installed_at) { $hist.installed_at.Substring(0, [Math]::Min(10, $hist.installed_at.Length)) } else { "Today" }
            $days = if ($null -ne $hist.lifetime.active_days) { $hist.lifetime.active_days } else { 1 }
            $script:contextMenu.Items.Add("  Tracking Since:   $installDate ($days days active)") | Out-Null
        }
        $script:contextMenu.Items.Add("-") | Out-Null
    }

    # Actions
    $itemDash = $script:contextMenu.Items.Add("Open Full Web Dashboard")
    $itemDash.Font = New-Object System.Drawing.Font "Segoe UI", 9, [System.Drawing.FontStyle]::Bold
    $itemDash.Add_Click({ Start-Process "http://127.0.0.1:8765" })

    $itemExit = $script:contextMenu.Items.Add("Exit PowerPulse Widget")
    $itemExit.Add_Click({
        $script:timer.Stop()
        $script:notifyIcon.Visible = $false
        [System.Windows.Forms.Application]::Exit()
    })
}

# Polling Timer
$script:timer = New-Object System.Windows.Forms.Timer
$script:timer.Interval = 1000

$script:timer.Add_Tick({
    try {
        $wc = New-Object System.Net.WebClient
        $wc.Headers.Add("User-Agent", "PowerPulse-Windows-Widget")
        $json = $wc.DownloadString($script:ApiUrl)
        $data = $json | ConvertFrom-Json

        $p = [Math]::Round($data.power.total_watts, 1)
        $cpu = [Math]::Round($data.cpu_usage_pct, 0)
        $gpu = if ($null -ne $data.gpu_usage_pct) { [Math]::Round($data.gpu_usage_pct, 0) } else { 8 }
        $ram = if ($null -ne $data.ram.pct) { [Math]::Round($data.ram.pct, 0) } else { 55 }
        $netText = if ($data.network.down_mbps -ge 1.0) { "$([Math]::Round($data.network.down_mbps, 1))M" } else { "$([Math]::Round($data.network.down_kbs, 0))K" }

        # Update Tray Tooltip (Max 63 chars on Windows API)
        $tooltip = "PowerPulse: ${p}W | CPU ${cpu}% | GPU ${gpu}% | RAM ${ram}% | $netText"
        if ($tooltip.Length -gt 63) { $tooltip = $tooltip.Substring(0, 63) }
        $script:notifyIcon.Text = $tooltip

        # Update Tray Menu
        Update-MenuUI $data
    } catch {
        Ensure-ServerRunning
        $script:notifyIcon.Text = "PowerPulse // Reconnecting..."
    }
})

# Double-click tray icon to open Web Dashboard
$script:notifyIcon.Add_DoubleClick({
    Start-Process "http://127.0.0.1:8765"
})

Ensure-ServerRunning
$script:timer.Start()
Update-MenuUI $null

# Keep Windows message pump active
[System.Windows.Forms.Application]::Run()
