import random
import time
import os

def play_game():
    choices = {
        "1": ("Rock", "🪨"),
        "2": ("Paper", "📄"),
        "3": ("Scissors", "✂️")
    }
    
    player_score = 0
    bot_score = 0
    
    print("=" * 45)
    print("   🎮 ROCK - PAPER - SCISSORS (VS AI) 🎮")
    print("=" * 45)
    print("Winning rules:")
    print("🪨 beats ✂️  |  📄 beats 🪨  |  ✂️ beats 📄\n")

    for round_num in range(1, 4):
        print(f"--- 🥊 ROUND {round_num} OF 3 ---")
        print("1. 🪨 Rock")
        print("2. 📄 Paper")
        print("3. ✂️ Scissors")
        
        user_input = input("Tomar choice (1/2/3): ").strip()
        if user_input not in choices:
            print("❌ Invalid choice! Round skipped.\n")
            continue
            
        user_name, user_emoji = choices[user_input]
        bot_key = random.choice(["1", "2", "3"])
        bot_name, bot_emoji = choices[bot_key]
        
        print("\nThinking...")
        time.sleep(0.5)
        print(f"You chose : {user_emoji} ({user_name})")
        print(f"AI chose  : {bot_emoji} ({bot_name})")
        
        if user_input == bot_key:
            print("🤝 Draw!")
        elif (user_input == "1" and bot_key == "3") or \
             (user_input == "2" and bot_key == "1") or \
             (user_input == "3" and bot_key == "2"):
            print("🎉 You won this round!")
            player_score += 1
        else:
            print("🤖 AI won this round!")
            bot_score += 1
        print(f"Current Score -> You: {player_score} | AI: {bot_score}\n")

    print("=" * 45)
    if player_score > bot_score:
        print("🏆 CONGRATULATIONS! You defeated the AI! 🎉")
    elif player_score < bot_score:
        print("🤖 AI Won! Better luck next time!")
    else:
        print("🤝 Match Tied!")
    print("=" * 45)

if __name__ == "__main__":
    play_game()
