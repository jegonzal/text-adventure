# Press the green Run button, then answer the questions down in the Shell.
#
# This is a "fill in the blanks" story: it asks you for a bunch of words
# (a color, a name, an animal, ...) and then drops them into a story that's
# already written below. Try changing the words in the story to make your
# own version!

from fun import *


clear()
banner("Malfunction Story")

color = ask("give me a color: ")
while "red" in color:
    say("I don't like red.")
    color = ask("give me a color: ")


name = ask("Give me a name: ")
animal = ask("Give me an animal: ")
food = ask("Give me a food: ")
say(f"I don't like {food}.")
food = ask("Give me a different food: ")

silly_word = ask("Give me a silly word: ")

place = ask("give me a place: ")
verb = ask("give me a verb: ")

write("Okay! Writing your story", "purple", speed=0.05)
drumroll()
clear()
banner(f"{animal} Malfunction")
say(f"{animal} malfunction")

# Paint each fill-in-the-blank word its own color, so it stands out from
# the rest of the story. If the color the player typed is one we know
# about (like "pink"), we use that color for the word itself!
name_c = paint(name, "pink")
animal_c = paint(animal, "orange")
food_c = paint(food, "green")
silly_word_c = paint(silly_word, "purple")
place_c = paint(place, "cyan")
verb_c = paint(verb, "yellow")
color_c = paint(color, color if color in COLORS else "white")

story = f"""
once upon a time there was a girl named {name_c}
she was attacked by an {animal_c}
Once upon a time. In a place called {place_c}.
There was a {name_c} who {verb_c} all the way to {silly_word_c} {place_c}.
One day {name_c} got attacked by a {animal_c} and they turned {color_c}.

A few days later {name_c} turned into a {food_c} and the {animal_c}
yelled {silly_word_c} and ate {name_c}.
"""

# say() types the story out on screen while reading it out loud, all
# at the same time.
say(story)