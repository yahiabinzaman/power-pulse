import math
import time
import os

def render_3d_donut(frames=80):
    A = 0
    B = 0
    
    print("\033[2J", end="") # Clear screen
    
    for _ in range(frames):
        z = [0] * 1760
        b = [' '] * 1760
        
        j = 0
        while j < 6.28:
            j += 0.07
            i = 0
            while i < 6.28:
                i += 0.02
                
                c = math.sin(i)
                d = math.cos(j)
                e = math.sin(A)
                f = math.sin(j)
                g = math.cos(A)
                h = d + 2
                D = 1 / (c * h * e + f * g + 5)
                l = math.cos(i)
                m = math.cos(B)
                n = math.sin(B)
                t = c * h * g - f * e
                
                x = int(40 + 30 * D * (l * h * m - t * n))
                y = int(12 + 15 * D * (l * h * n + t * m))
                o = int(x + 80 * y)
                N = int(8 * ((f * e - c * d * g) * m - c * d * e - f * g - l * d * n))
                
                if 0 <= y < 22 and 0 <= x < 80 and D > z[o]:
                    z[o] = D
                    b[o] = ".,-~:;=!*#$@"[max(0, N)]
                    
        print("\033[H", end="") # Move to home
        print("\033[93m--- 🍩 3D SPINNING DONUT ANIMATION (Python Math) 🍩 ---\033[0m\n")
        output = ""
        for k in range(1760):
            output += b[k] if k % 80 else "\n"
        print("\033[96m" + output + "\033[0m")
        
        A += 0.08
        B += 0.04
        time.sleep(0.03)

if __name__ == "__main__":
    try:
        render_3d_donut(frames=120)
    except KeyboardInterrupt:
        print("\nAnimation Stopped.")
