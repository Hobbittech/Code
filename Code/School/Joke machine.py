print("What would you like to joke about? ") 

topic = input() 

 

if topic == "hippos": 

     print("Why do you never see hippos hiding in trees?") 

     answer = "because they're very good at it" 

     guess = input() 

     if answer == guess: 

          print("That's correct") 

     else: 

          print(answer) 


if topic == "prehistoric": 

     print("What were prehistoric sleepovers called?") 

     answer = "Dino-SNORES."  

     guess = input() 

     if answer == guess: 

          print("That's correct") 

     else: 

          print(answer) 


if topic == "cows": 

     print("What kind of cow wears a crown?") 

     answer = "A dairy queen."  

     guess = input() 

     if answer == guess: 

          print("That's correct") 

     else: 

          print(answer) 


if topic == "desserts": 

     print("What do turkeys like to eat for dessert?") 

     answer = "Apple Gobbler"  

     guess = input() 

     if answer == guess: 

          print("That's correct") 

     else: 

          print(answer) 


if topic == "desserts": 

     print("Why do storks have so little money?") 

     answer = "They have such big bills."  

     guess = input() 

     if answer == guess: 

          print("That's correct") 

     else: 

          print(answer) 
else: 

    print("I'm sorry, I don't have a joke about", topic) 