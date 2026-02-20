while True:
    print("Welcome to Python Volume calcualator")
    print("Ctrl+c to exit don't worry if ti crashes")
    print("Insert your unit AND your three measurements to get the volume")
    user_unit = input("Type your unit")
    user_calc_1 = float(input("Your first measurement without unit"))
    user_calc_2 = float(input("Your second measurement without unit"))
    user_calc_3 = float(input("Your third measurement without unit"))
    user_volume = user_calc_1*user_calc_2*user_calc_3
    print(f"Your total volume for your shape is {user_volume}{user_unit}.")
    print()
    print(f"Your unit was {user_unit}")
    print()
    print(f"Your first measurement was {user_calc_1}")
    print()
    print(f"Your second measurement was {user_calc_2}")
    print()
    print(f"And finally, your third measurement was {user_calc_3}")

