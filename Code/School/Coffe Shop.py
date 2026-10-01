print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
print("+                               +")
print("+         The Coffee Shop       +")
print("+              Welcome          +")
print("+                               +")
print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
print("")
print("We serve the following coffees:")
print(" > Espresso")
print(" > Americano")
print(" > Latte")
print(" > Cappuccino")
print(" > Macchiato")
print(" > Mocha")
print(" > Flat White")
print("----------------------------")

price = 0
coffee = input("What type of coffee would you like?")

if coffee=="Espresso":
   price = price + 2.50
elif coffee=="Americano":
   price = price + 3
elif coffee == "Latte":
   price = price + 2.50
elif coffee == "Cappuccino":
   price = price + 3.00
elif coffee == "Macchiato":
   price = price + 2.50
elif coffee == "Mocha":
   price = price + 3.50
elif coffee == "Flat White":
   price = price + 2.50 

size = input("What size would you like?")

if size=="Medium":
   price = price + 0.00
elif size=="Large":
   price = price + 1.00
elif size=="XL":
   price = price + 1.50

Location = input("Eat in or take away")

if Location=="Eat in":
   price = price + 0.00
elif size=="Take away":
   price = price + 1.00


print("----------------------------")
print("Total Cost: £" + str(price))
