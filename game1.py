# Press the green Run button, then answer the questions down in the Shell.
#
# The Troll Bridge: a grumpy troll won't let you cross his bridge unless
# you give him a present. But this troll is weird -- he only likes
# STINKY, GROSS presents! The oracle() decides if your present is gross
# enough.

from fun import *

banner("The Troll Bridge")

say("What is your name, brave hero?")
name = ask("Name: ")

say(f"{name} comes to a rickety old bridge over a bubbling river.")
say("A grumpy troll jumps out from underneath it!", color="green")
say("'Nobody crosses MY bridge without giving me a present!' he growls.", color="green")
say("'And I only like presents that are STINKY and GROSS!'", color="green")

tries = 0

passed = False
while not passed:
    present = ask("What present do you give the troll? ")
    tries = tries + 1
    say(f"{name} hands the troll {present}.")
    drumroll()

    if oracle(f"Would most kids say 'ew, gross!' about {present}?"):
        say(f"The troll sniffs {present}...")
        say("'Ooooh! It's DISGUSTING! I LOVE it!'", color="green")
        passed = True
    else:
        say(f"The troll sniffs the {present}...")
        say(f"'BLEH! That {present} smells NICE! Yuck!'", color="green")
        say(f"The troll throws the {present} into the river. SPLASH!", color="blue")
        say(f"'Try again! And make it GROSSER!'", color="green")

say("The troll gives you a big slimy hug and lets you cross the bridge.")
say(f"It took {name} {tries} tries to make the troll happy.")
banner("You crossed the bridge!", "green")


say(f"{name} comes to a large brick wall.")
say("A proud wizard stands before the wall, arms crossed.", color="blue")
say("'Nobody crosses MY wall without guessing my favorite number' he proclaims.", color="blue")
say("'It is a number between 1 and 100!'", color="blue")
say("'If you guess my number correctly, you may pass!'", color="blue")
say("'If you guess wrong I will say whether my number is higher or lower!'", color="blue")
say("'But after 7 questions, I will pick another number!'", color="blue")


passed = False
total_tries = 0

while not passed:
    magic_number = dice(100)
    for tries in range(7):
        total_tries += 1
        guess = ask("What is my number? ", type="number")
        drumroll()
        if guess == magic_number:
            say(f"The wizard claps his hands and says, 'Correct! You may pass.'", color="blue")
            passed = True
            break
        elif guess < magic_number:
            say(f"'My number is HIGHER than {guess}!'", color="blue")
        else:
            say(f"'My number is LOWER than {guess}!'", color="blue")
    if not passed:
        say(f"The wizard sighs and picks a new number.", color="blue")

say("The wizard lets you pass through the wall.")
say(f"It took {name} {total_tries} tries to guess the wizard's number.")
