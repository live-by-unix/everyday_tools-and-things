import os

#Start Logic
print('Welcome to Caffine!')
print("Caffine is a tool which keeps your Mac computer awake and never puts any part of it to sleep.")
print()

the_instruct = """Simply type 'coffeeup' to make your computer NEVER sleep or stop doing anything. Type 'coffeedown' to restore the ability to sleep to your computer."""
user_input = input("Simply type 'coffeeup' to make your computer NEVER sleep or stop doing anything. Type 'coffeedown' to restore the ability to sleep to your computer.").strip().lower()

if user_input == 'coffeeup':
    os.system("pmset -f idle -s 0")
elif user_input == 'coffeedown':
    os.system("osascript -e 'tell application System Events to set the idle timer to 60'")
else:
    print(f"Unknown command. Here is how caffinate works {the_instruct}")        
