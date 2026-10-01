
tables = int(input("What times tables do u want to know:"))
start = int(input("Enter the number you want the time table to start at: "))
end = int(input("Enter the number you want the time tables to end at:"))
for x in range(tables, end + 1, tables):
        print(x)