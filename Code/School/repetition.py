number = 6
guess = int(input("Guess the number: "))

while guess!=number:
    print("Try again")
    guess = int(input("Guess the number: "))
print("Good job")