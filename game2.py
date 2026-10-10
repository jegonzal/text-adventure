# Press the green Run button, then answer the questions down in the Shell.
#
# The Wizard's Lost Hat: a bigger adventure. You explore a wizard's
# castle one room at a time. In each room there's a problem, and you can
# type ANYTHING you want to do about it. The oracle() decides if your
# idea works, a dice() roll adds some luck, and imagine() tells you what
# happened. Every idea you try is saved into a story you can keep.
#
# Ideas for making it your own:
#   - Add a new room to the ROOMS list (copy one and change it).
#   - Give the player more hearts, or fewer if you like it hard.
#   - Change what counts as a lucky roll.

from fun import *

# Each room has a problem to solve, and a treasure you get for solving it.
ROOMS = [
    {
        "name": "the Kitchen",
        "problem": "a giant, grumpy cat is sitting in front of the door and hissing at anyone who comes near",
        "treasure": "a rubber duck",
    },
    {
        "name": "the Library",
        "problem": "hundreds of flying books are swooping around like angry birds and won't let anyone through",
        "treasure": "a jar of glowing jelly",
    },
    {
        "name": "the Tower",
        "problem": "a sleepy dragon is curled around the wizard's lost hat and snores out little puffs of fire",
        "treasure": "the wizard's lost hat",
    },
]

hearts = 4
backpack = []
story = []  # Everything that happens, so we can save it at the end.

banner("The Wizard's Lost Hat", "purple")
name = ask("What is your name, brave hero? ")
say(f"Welcome, {name}! The wizard has lost a very important hat somewhere in this castle.", color="purple")
say("Every room has a problem. Type anything you want to try -- the sillier the better!", color="purple")

for room in ROOMS:
    if hearts == 0:
        break

    banner(room["name"], "yellow")
    scene = imagine(f"In 2 sentences, describe what the hero {name} sees walking into {room['name']} of a wizard's castle, where {room['problem']}.")
    say(scene)
    story.append(scene)

    solved = False
    while not solved and hearts > 0:
        print()
        print(paint("Hearts: " + "<3 " * hearts, "red"))
        if backpack:
            print(paint("Backpack: " + ", ".join(backpack), "cyan"))
        else:
            print(paint("Backpack: (empty)", "cyan"))

        idea = ask("What do you do? ")
        story.append(f"{name} tried: {idea}")

        # Roll a 20-sided die for a bit of luck.
        write("You roll the dice of fate...", "yellow")
        drumroll()
        roll = dice(20)
        write(f"You rolled a {roll}!", "yellow")

        if roll == 20:
            write("A PERFECT roll! Your idea works no matter what!", "green")
            solved = True
        elif roll == 1:
            write("Oh no, a 1! Something goes terribly wrong...", "red")
            solved = False
        else:
            if backpack:
                carrying = "They are carrying: " + ", ".join(backpack) + "."
            else:
                carrying = "They are not carrying anything."
            solved = oracle(
                f"In a silly fantasy adventure for kids, the hero is in {room['name']}, where "
                f"{room['problem']}. {carrying} The hero tries this: '{idea}'. "
                f"Players should usually win when their idea is kind, clever, or funny, "
                f"and lose when it is lazy, mean, or makes no sense. Does this idea work?"
            )

        if solved:
            result = imagine(f"In 2 or 3 funny sentences, describe how {name} solves this problem: {room['problem']}. They do it by trying this: '{idea}'. At the end, they find {room['treasure']}.")
            say(result, color="green")
            say(f"You found {room['treasure']}!", color="cyan")
            backpack.append(room["treasure"])
        else:
            result = imagine(f"In 2 funny sentences, describe how {name}'s plan goes wrong. The problem: {room['problem']}. What they tried: '{idea}'. Nobody gets hurt -- the plan just flops in a silly way.")
            say(result, color="orange")
            hearts = hearts - 1
        story.append(result)

if hearts > 0:
    ending = imagine(f"In 3 sentences, describe the wizard's joyful thank-you party for {name}, who found the wizard's lost hat. Mention these things the hero collected: {', '.join(backpack)}.")
    say(ending, color="purple")
    banner("You win!", "green")
else:
    ending = imagine(f"In 2 sentences, describe {name} being gently carried out of the wizard's castle by a team of helpful mice, ready to try again tomorrow.")
    say(ending, color="purple")
    banner("Game over", "red")
story.append(ending)

save_story(f"{name} and the Wizard's Lost Hat", "\n\n".join(story))
write("Your adventure was saved in finished_stories.txt!", "cyan")
