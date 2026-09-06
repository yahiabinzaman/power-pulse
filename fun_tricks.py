import time
import sys
import math

def print_banner():
    print("=" * 50)
    print("      ✨ PYTHON ER MOJAR TRICKS & CODES ✨      ")
    print("=" * 50)

# Trick 1: Swap two variables without temporary variable
def swap_trick():
    print("\n1️⃣ Variable Swap (Without 3rd variable):")
    a, b = "Tea ☕", "Coffee 🍵"
    print(f"Before -> a: {a}, b: {b}")
    a, b = b, a
    print(f"After  -> a: {a}, b: {b}")

# Trick 2: Typing Animation Effect
def typing_effect(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# Trick 3: Mathematical Heart Pattern
def draw_math_heart():
    print("\n3️⃣ Math Heart Formula:")
    for y in range(12, -12, -1):
        line = ""
        for x in range(-30, 30):
            # Formula: (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
            x_scaled = x * 0.04
            y_scaled = y * 0.1
            if (x_scaled**2 + y_scaled**2 - 1)**3 - (x_scaled**2) * (y_scaled**3) <= 0:
                line += "❤️"
            else:
                line += " "
        if "❤️" in line:
            print(line)

# Trick 4: Emoji & String Multiplications
def emoji_pyramid(rows=5):
    print("\n4️⃣ Emoji Pyramid:")
    for i in range(1, rows + 1):
        spaces = " " * (rows - i) * 2
        fire = "🔥" * (2 * i - 1)
        print(f"{spaces}{fire}")

# Trick 5: Python One-Liner Palindrome Checker
def palindrome_check():
    print("\n5️⃣ One-Liner Palindrome Checker:")
    words = ["madam", "python", "racecar", "bangladesh"]
    for w in words:
        is_pal = w == w[::-1]
        status = "✅ Palindrome" if is_pal else "❌ Not Palindrome"
        print(f" - {w:<12} -> {status}")

if __name__ == "__main__":
    print_banner()
    swap_trick()
    
    print("\n2️⃣ Typewriter Effect:")
    typing_effect(">> Python is simple, powerful and incredibly fun! 🚀")
    
    emoji_pyramid()
    draw_math_heart()
    palindrome_check()
