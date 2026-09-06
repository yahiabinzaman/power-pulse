# ==========================================
# Welcome to Python Practice!
# ==========================================

def greet(name):
    return f"Hello, {name}! Welcome to Python programming."

if __name__ == "__main__":
    user_name = "Coder"
    print(greet(user_name))
    
    # Simple calculation example
    numbers = [1, 2, 3, 4, 5]
    print(f"Numbers: {numbers}")
    print(f"Sum: {sum(numbers)}")
    print(f"Squares: {[x**2 for x in numbers]}")
