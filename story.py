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


story = f"""
once upon a time there was a girl named {name}
she was attacked by an {animal}
Once upon a time. In a place called {place}. 
There was a {name} who {verb} all the way to {silly_word} {place}.
One day {name} got attacked by a {animal} and they turned {color}.

A few days later {name} turned into a {food} and the {animal} 
yelled {silly_word} and ate {name}.
"""


write(story, "green")
say(story)