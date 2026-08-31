import Cocoa
import Foundation

// Structs for JSON Telemetry
struct PowerData: Codable {
    let total_watts: Double
    let cpu_watts: Double
    let gpu_watts: Double
    let base_watts: Double
    let peak_watts: Double
    let min_watts: Double
    let avg_watts: Double
}

struct ProcessItem: Codable {
    let pid: String
    let name: String
    let watts: Double?
    let cpu: Double
    let mem: Double
}

struct NetworkData: Codable {
    let down_mbps: Double
    let up_mbps: Double
    let ping_ms: Double
    let down_kbs: Double
    let up_kbs: Double
}

struct TelemetryResponse: Codable {
    let power: PowerData
    let cpu_usage_pct: Double
    let processes: [ProcessItem]?
    let network: NetworkData?
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem!
    var timer: Timer?
    var showNetInBar: Bool = true
    
    // Motijheel Highest Peak Electricity Tariff: ৳13.44 + 5% VAT = ৳14.11 / unit
    var tariffRate: Double = 14.11
    var currencySymbol: String = "৳"

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Run as menu bar accessory without dock icon
        NSApp.setActivationPolicy(.accessory)

        // Create Status Item in macOS Menu Bar
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        
        if let button = statusItem.button {
            button.title = "--W"
            button.font = NSFont.monospacedSystemFont(ofSize: 12, weight: .medium)
        }

        buildInitialMenu()

        // Fetch telemetry every 1.0 second
        timer = Timer.scheduledTimer(timeInterval: 1.0, target: self, selector: #selector(fetchTelemetry), userInfo: nil, repeats: true)
        RunLoop.main.add(timer!, forMode: .common)
        
        fetchTelemetry()
    }

    func buildInitialMenu() {
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "CYBER_VOLT // macOS Live Telemetry", action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Connecting to Telemetry Engine...", action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Open Full Web Dashboard", action: #selector(openDashboard), keyEquivalent: "d"))
        menu.addItem(NSMenuItem(title: "Display Mode: [Watts + Net]", action: #selector(toggleMode), keyEquivalent: "t"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "System Architect: Yahia Bin Zaman", action: #selector(openGithub), keyEquivalent: "g"))
        menu.addItem(NSMenuItem(title: "Quit", action: #selector(quitApp), keyEquivalent: "q"))
        statusItem.menu = menu
    }

    @objc func toggleMode() {
        showNetInBar.toggle()
        fetchTelemetry()
    }

    @objc func openDashboard() {
        if let url = URL(string: "http://127.0.0.1:8765") {
            NSWorkspace.shared.open(url)
        }
    }

    @objc func openGithub() {
        if let url = URL(string: "https://github.com/yahiabinzaman") {
            NSWorkspace.shared.open(url)
        }
    }

    @objc func openFacebook() {
        if let url = URL(string: "https://facebook.com/yahiabinzaman") {
            NSWorkspace.shared.open(url)
        }
    }

    @objc func quitApp() {
        NSApplication.shared.terminate(nil)
    }

    @objc func fetchTelemetry() {
        guard let url = URL(string: "http://127.0.0.1:8765/api/telemetry") else { return }
        
        var request = URLRequest(url: url)
        request.timeoutInterval = 1.5
        
        let task = URLSession.shared.dataTask(with: request) { [weak self] (data, response, error) in
            guard let self = self else { return }
            
            DispatchQueue.main.async {
                if let data = data, let telemetry = try? JSONDecoder().decode(TelemetryResponse.self, from: data) {
                    self.updateUI(with: telemetry)
                } else {
                    if let button = self.statusItem.button {
                        button.title = "Offline"
                    }
                }
            }
        }
        task.resume()
    }

    func updateUI(with data: TelemetryResponse) {
        let p = data.power
        let net = data.network
        
        // 1. Update Status Bar Title (Minimal, Clean Monospace)
        if let button = statusItem.button {
            if showNetInBar, let n = net {
                let netText = n.down_mbps >= 1.0 ? String(format: "%.1fM", n.down_mbps) : String(format: "%.0fK", n.down_kbs)
                button.title = String(format: "%.1fW  |  %@", p.total_watts, netText)
            } else {
                button.title = String(format: "%.1fW", p.total_watts)
            }
        }

        // 2. Build Interactive Clean Dropdown Menu (No Emojis)
        let menu = NSMenu()
        
        // Header
        let header = NSMenuItem(title: "CYBER_VOLT // LIVE TELEMETRY", action: nil, keyEquivalent: "")
        header.isEnabled = false
        menu.addItem(header)
        menu.addItem(NSMenuItem.separator())

        // Power Telemetry Section
        let totalPwr = NSMenuItem(title: String(format: "Total Power Draw: %.2f Watts", p.total_watts), action: nil, keyEquivalent: "")
        totalPwr.attributedTitle = NSAttributedString(string: String(format: "Total Power Draw: %.2f Watts", p.total_watts), attributes: [.font: NSFont.boldSystemFont(ofSize: 13)])
        menu.addItem(totalPwr)

        menu.addItem(NSMenuItem(title: String(format: "  CPU Package: %.1f W (Load: %.1f%%)", p.cpu_watts, data.cpu_usage_pct), action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: String(format: "  GPU & Neural Engine: %.1f W", p.gpu_watts), action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: String(format: "  RAM & SoC Base Load: %.1f W", p.base_watts), action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: String(format: "  Min: %.1fW | Avg: %.1fW | Peak: %.1fW", p.min_watts, p.avg_watts, p.peak_watts), action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())

        // Internet Speed Section
        if let n = net {
            let netHeader = NSMenuItem(title: "Network Telemetry", action: nil, keyEquivalent: "")
            netHeader.attributedTitle = NSAttributedString(string: "Network Telemetry", attributes: [.font: NSFont.boldSystemFont(ofSize: 12)])
            menu.addItem(netHeader)
            menu.addItem(NSMenuItem(title: String(format: "  Download: %.2f Mbps (%.1f KB/s)", n.down_mbps, n.down_kbs), action: nil, keyEquivalent: ""))
            menu.addItem(NSMenuItem(title: String(format: "  Upload: %.2f Mbps (%.1f KB/s)", n.up_mbps, n.up_kbs), action: nil, keyEquivalent: ""))
            menu.addItem(NSMenuItem(title: String(format: "  Ping Latency: %.1f ms", n.ping_ms), action: nil, keyEquivalent: ""))
            menu.addItem(NSMenuItem.separator())
        }

        // Electricity Cost Section - Motijheel Peak Rate (৳14.11 / unit)
        let kw = p.total_watts / 1000.0
        let costHr = kw * tariffRate
        let costDay = costHr * 24.0
        let costMo = costHr * 24.0 * 30.0
        let costHeader = NSMenuItem(title: "Electricity Cost (Motijheel Peak @ ৳14.11/kWh)", action: nil, keyEquivalent: "")
        costHeader.attributedTitle = NSAttributedString(string: "Electricity Cost (Motijheel Peak @ ৳14.11/kWh)", attributes: [.font: NSFont.boldSystemFont(ofSize: 12)])
        menu.addItem(costHeader)
        menu.addItem(NSMenuItem(title: String(format: "  Cost / Hour: %@ %.3f", currencySymbol, costHr), action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: String(format: "  24h Nonstop: %@ %.2f / day", currencySymbol, costDay), action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: String(format: "  Monthly Est: %@ %.2f (30d Peak)", currencySymbol, costMo), action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())

        // Top App Consumer
        if let procs = data.processes, !procs.isEmpty {
            let topApp = procs[0]
            menu.addItem(NSMenuItem(title: String(format: "Top Application: %@ (%.2f W)", topApp.name, topApp.watts ?? 0.0), action: nil, keyEquivalent: ""))
            menu.addItem(NSMenuItem.separator())
        }

        // Action Controls
        menu.addItem(NSMenuItem(title: "Open Full Web Dashboard", action: #selector(openDashboard), keyEquivalent: "d"))
        let toggleItem = NSMenuItem(title: showNetInBar ? "Display Mode: [Watts + Net]" : "Display Mode: [Watts Only]", action: #selector(toggleMode), keyEquivalent: "t")
        menu.addItem(toggleItem)
        menu.addItem(NSMenuItem.separator())

        // Clean Architect Credits (Minimal)
        let creditHeader = NSMenuItem(title: "System Architect: Yahia Bin Zaman", action: nil, keyEquivalent: "")
        creditHeader.attributedTitle = NSAttributedString(string: "System Architect: Yahia Bin Zaman", attributes: [.font: NSFont.boldSystemFont(ofSize: 11)])
        menu.addItem(creditHeader)
        menu.addItem(NSMenuItem(title: "  GitHub: github.com/yahiabinzaman", action: #selector(openGithub), keyEquivalent: "g"))
        menu.addItem(NSMenuItem(title: "  Facebook: facebook.com/yahiabinzaman", action: #selector(openFacebook), keyEquivalent: "f"))
        menu.addItem(NSMenuItem.separator())

        menu.addItem(NSMenuItem(title: "Quit Status Bar", action: #selector(quitApp), keyEquivalent: "q"))

        statusItem.menu = menu
    }
}

// Application Entry Point
let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
