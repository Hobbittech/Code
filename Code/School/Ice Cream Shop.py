print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
print("+                               +")
print("+      The Ice Cream Shop       +")
print("+            Welcome            +")
print("+                               +")
print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
print("")
price = 0
container = input("What type of ice cream container would you like: cup or cone?")
if container == "cup":
    price = price + 0.50
elif container == "cone":
    price = price + 0.80
else:
    print("Invalid option!")

Scoops = input("How many scoops do you want?")
if Scoops == "cup":
    price = price + 0.50
elif Scoops == "cone":
    price = price + 0.80
else:
    print("Invalid option!")


