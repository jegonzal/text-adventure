# Press the green Run button, then answer the questions down in the Shell.
#
# This is a choose-your-own-weapon adventure: you fight a dragon and earn
# or lose points depending on what you choose and what the oracle() thinks
# of your answers.

from fun import *

points = 0
has_won = False
while not has_won:
    say("Welcome to Fairyland")

    say("What is your name")
    name = ask("name? ")

    say(f"Welcome {name}, are you ready for an adventure?")

    ready = ask("Ready: ")

    if oracle(f"I asked the user if they are ready for an adventure and they said '{ready}'. Are they ready?"):
        say("Great, you didn't have a choice anyways. But because you said yes you get one point.")
        points = points + 1
        say(f"Your score is now {points}.")        
    else:
        say("Too bad and you lost a point.")
        points = points - 1
        say(f"Your score is now {points}.")


    say("A dragon has landed in front of you. Choose your weapon")
    
    weapon = ask("Choose a weapon: ")
    say(f"{name} picked up the {weapon} and threw it at the dragon.")

    while oracle(f"Is {weapon} a food?"):
        say(f"The dragon ate the {weapon}.")
        points = points - 1
        say(f"Your score is now {points}. Choose another weapon.")
        weapon = ask("Choose another weapon: ")
        say(f"{name} picked up the {weapon} and threw it at the dragon.")

    say(f"{name} stunned the dragon with the {weapon}")
    points = points + 5
    say(f"Your score is now {points}.")


    say("You Win!")
    has_won = True



