import time
import os
import random
import shutil

# ANSI Color Codes
GREEN = "\033[92m"
BRIGHT_GREEN = "\033[1;32m"
WHITE = "\033[1;37m"
RESET = "\033[0m"

def matrix_rain(duration_sec=10):
    os.system('cls' if os.name == 'nt' else 'clear')
    columns, _ = shutil.get_terminal_size((80, 24))
    
    # Random characters
    chars = "0123456789ABCDEFabcdef!@#$%^&*()_+-=[]{}|;:,.<>?"
    drops = [0] * columns
    
    print(f"{BRIGHT_GREEN}Entering the Matrix... (Running for {duration_sec}s | Press Ctrl+C to stop){RESET}")
    time.sleep(1)

    start_time = time.time()
    try:
        while time.time() - start_time < duration_sec:
            line = ""
            for i in range(columns):
                if random.random() > 0.90:
                    char = random.choice(chars)
                    # Mix of bright leading characters and green body
                    color = WHITE if random.random() > 0.8 else (BRIGHT_GREEN if random.random() > 0.5 else GREEN)
                    line += f"{color}{char}{RESET}"
                else:
                    line += " "
            print(line)
            time.sleep(0.04)
    except KeyboardInterrupt:
        pass
    finally:
        print(f"\n{BRIGHT_GREEN}Matrix Simulation Ended.{RESET}\n")

if __name__ == "__main__":
    matrix_rain(duration_sec=12)
