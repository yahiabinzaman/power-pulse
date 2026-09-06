import time
import os
import math

# ANSI Colors
RED = "\033[91m"
PINK = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def render_heart(scale, color):
    lines = []
    # Heart curve: (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
    for y in range(12, -11, -1):
        line = ""
        for x in range(-25, 26):
            x_val = x * 0.05 / scale
            y_val = y * 0.1 / scale
            if (x_val**2 + y_val**2 - 1)**3 - (x_val**2) * (y_val**3) <= 0:
                line += "❤️"
            else:
                line += "  "
        if "❤️" in line:
            lines.append(line)
    return lines

def pulse_heart_animation(cycles=6):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{BOLD}💓 Pulsing Heart Animation (Python Math & ANSI) 💓{RESET}\n")
    
    # Scale oscillations for heartbeat rhythm (lub-dub)
    scales = [0.85, 0.95, 1.15, 1.0, 1.25, 1.05, 0.9, 0.85]
    
    for _ in range(cycles):
        for s in scales:
            lines = render_heart(s, RED if s > 1.0 else PINK)
            # Clear previous frame
            print("\033[H", end="")  # Move cursor to top-left
            print("\n" * max(0, int((1.3 - s) * 3))) # vertical bounce
            for l in lines:
                print(f"      {l}")
            time.sleep(0.12)
            
    print(f"\n\n      {BOLD}{PINK}✨ Heartbeat Animation Complete! ✨{RESET}\n")

if __name__ == "__main__":
    pulse_heart_animation(cycles=5)
