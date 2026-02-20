import time
from datetime import datetime


print("Welcome to the Python Weather App!")
print("Exit via CTRL+C")

while True:
    try:
        print("\n" + "="*30)
        user_input = float(input("Put your weather in Fahrenheit (°F): "))
        user_city = input("Input your city please: ")

        if user_input > 134 or user_input < -134:
            print("WOW. BETTER STAY HOME. YOU'RE ON VENUS OR LIKE NEPTUNE.")
        elif user_input >= 100: 
             print("Wow what a scorcher! Better stay home with the AC.")
        elif user_input >= 80:
             print("It's a hot day! Perfect for a swim.")
        elif user_input >= 60:
             print("A nice warm day. Perfect for a walk.")
        elif user_input >= 40:
             print("Wooh yeah! It's a bit chilly. Remember your sweater.")     
        elif user_input >= 10:
             print("It's cold alright! Wear a heavy coat.")
        elif user_input >= -25:
             print("Stay home with the heater and hot cocoa.")
        else:
             print("COLD. HOPE YOU SURVIVE.")

        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{now}] City: {user_city} | Temp: {user_input}°F\n"

        with open("weather_history.txt", "a") as file:
            file.write(log_entry)

        print(f"\nLogged to weather_history.txt Restarting in 5 seconds :)")
        time.sleep(5)

    except ValueError:
        
        print("\n[!] ERROR: Please enter a valid number for temperature you hacker.")
        time.sleep(1)
        
    except KeyboardInterrupt:
      
        print("\n\nThank you for using Python Weather App 1.0!")
        break