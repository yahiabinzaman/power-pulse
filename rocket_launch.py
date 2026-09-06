import time
import os
import random

# Colors
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"

ROCKET = [
    f"{RED}   /\\   {RESET}",
    f"{WHITE}  /  \\  {RESET}",
    f"{WHITE} | == | {RESET}",
    f"{CYAN} |    | {RESET}",
    f"{CYAN} |PYTHON|{RESET}",
    f"{WHITE} | == | {RESET}",
    f"{RED} / || \\ {RESET}",
    f"{YELLOW}/_ || _\\{RESET}"
]

EXHAUSTS = [
    [f"{YELLOW}   🔥   {RESET}", f"{RED}  🔥🔥  {RESET}"],
    [f"{RED}   🔥   {RESET}", f"{YELLOW} 🔥🔥🔥 {RESET}"],
    [f"{YELLOW}  🔥🔥  {RESET}", f"{RED} 🔥🔥🔥🔥{RESET}"]
]

def clear_screen():
    print("\033[H\033[J", end="")

def launch_rocket():
    clear_screen()
    print(f"{BOLD}{CYAN}🚀 MISSION: PYTHON ROCKET LAUNCH 🚀{RESET}\n")
    
    # 1. Countdown
    for count in [3, 2, 1]:
        print(f"       T-Minus {count}...")
        time.sleep(1)
        
    print(f"       {BOLD}{RED}IGNITION & LIFTOFF! 💥{RESET}\n")
    time.sleep(0.8)

    height = 18
    for pos in range(height, -10, -1):
        clear_screen()
        # Top padding pushes rocket down or lets it fly up
        if pos > 0:
            print("\n" * pos)
            for part in ROCKET:
                print(" " * 20 + part)
            for ex in random.choice(EXHAUSTS):
                print(" " * 20 + ex)
        elif pos <= 0 and pos > -len(ROCKET):
            # Rocket moving out of top
            visible_parts = ROCKET[-pos:]
            for part in visible_parts:
                print(" " * 20 + part)
            for ex in random.choice(EXHAUSTS):
                print(" " * 20 + ex)
        time.sleep(0.08)

    # 2. Fireworks in Space
    fireworks = [
        "       ✨ . * . 🌟  . *",
        "    💥 . * 🎆  BOOM! 🎆 * .",
        "  ✨  *  .  🌟  *  .  ✨",
        "      🎆 MISSION SUCCESS! 🎆"
    ]
    colors = [RED, YELLOW, GREEN, CYAN, MAGENTA, WHITE]
    
    for _ in range(8):
        clear_screen()
        print("\n" * 5)
        for line in fireworks:
            c = random.choice(colors)
            print(f"          {BOLD}{c}{line}{RESET}")
        time.sleep(0.25)
        
    print(f"\n\n{BOLD}{GREEN}      🚀 Welcome to the Python Space! 🛰️{RESET}\n")

if __name__ == "__main__":
    launch_rocket()
