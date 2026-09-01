"""
PowerPulse - Desktop Web Application Server
Serves real-time telemetry API and interactive Dashboard UI.
Pure Python standard library implementation for 100% zero-dependency cross-platform support.
"""

import os
import sys
import json
import time
import socket
import webbrowser
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

from power_engine import PowerEngine

PORT = 8765
HOST = "127.0.0.1"

# Initialize Telemetry Engine
engine = PowerEngine()

# Background telemetry updater thread
latest_telemetry = {}
telemetry_lock = threading.Lock()

def background_sampler():
    global latest_telemetry
    while True:
        try:
            sample = engine.sample_telemetry()
            with telemetry_lock:
                latest_telemetry = sample
        except Exception as e:
            print(f"[PowerEngine Error] {e}", file=sys.stderr)
        time.sleep(1.0)

# Start background thread
sampler_thread = threading.Thread(target=background_sampler, daemon=True)
sampler_thread.start()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class PowerPulseHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Base directory pointing to static folder
        self.static_dir = os.path.join(os.path.dirname(__file__), "static")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        # API Endpoints
        if self.path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            
            with telemetry_lock:
                data = latest_telemetry if latest_telemetry else engine.sample_telemetry()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        elif self.path == "/api/hardware":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(engine.system_info).encode("utf-8"))
            return

        elif self.path == "/api/speedtest":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            res = engine.run_speedtest_benchmark()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # Serve Frontend Assets
        if self.path == "/" or self.path == "/index.html":
            file_path = os.path.join(self.static_dir, "index.html")
            content_type = "text/html; charset=utf-8"
        elif self.path.startswith("/"):
            rel_path = self.path.lstrip("/")
            file_path = os.path.join(self.static_dir, rel_path)
            if file_path.endswith(".css"):
                content_type = "text/css"
            elif file_path.endswith(".js"):
                content_type = "application/javascript"
            elif file_path.endswith(".json"):
                content_type = "application/json"
            elif file_path.endswith(".svg"):
                content_type = "image/svg+xml"
            elif file_path.endswith(".png"):
                content_type = "image/png"
            elif file_path.endswith(".ico"):
                content_type = "image/x-icon"
            else:
                content_type = "text/plain"
        else:
            self.send_error(404, "Not Found")
            return

        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(os.path.getsize(file_path)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

    def log_message(self, format, *args):
        # Silence verbose GET spam in console for clean UI output
        pass

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, port)) == 0

def find_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def run_app():
    global PORT
    PORT = find_available_port(PORT)
    server_url = f"http://{HOST}:{PORT}"

    server = ThreadedHTTPServer((HOST, PORT), PowerPulseHandler)
    print("\n" + "="*56)
    print(" ⚡ PowerPulse - Real-time Computer Power Monitor ⚡ ")
    print("="*56)
    print(f" Platform : {engine.system_info['os']} ({engine.system_info['cpu_brand']})")
    print(f" Web UI   : {server_url}")
    print("="*56)
    print(" Dashboard is launching in your default browser...")
    print(" Press Ctrl+C to stop the monitor.\n")

    # Auto open browser after brief delay
    threading.Timer(0.8, lambda: webbrowser.open(server_url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[PowerPulse] Shutting down gracefully...")
        server.server_close()
        sys.exit(0)

if __name__ == "__main__":
    run_app()
