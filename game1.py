# Press the green Run button, then answer the questions down in the Shell.
#
# The Troll Bridge: the simplest adventure you can make with the oracle.
# A troll blocks the bridge, and you have to give it a present. The
# oracle() decides if the troll likes it, and imagine() makes up what
# happens next -- so the story is different every time you play!

from fun import *

banner("The Troll Bridge")

passed = False



while not passed:
    say("You come to a rickety old bridge over a bubbling river.")
    say("A grumpy troll jumps out from underneath it!", color="green")
    say("'Nobody crosses MY bridge without giving me a present!' it growls.", color="green")
    present = ask("What present do you give the troll? ")
    if oracle(f"Would a grumpy troll who lives under a bridge like getting {present} as a present?"):    
        passed = True
    else:
        story = imagine(f"In 2 or 3 sentences, describe a grumpy troll who HATES the {present} it was just given, and chases the hero away from its bridge.")
        say(story)
        banner("The troll chased you away!", "red")
    
story = imagine(f"In 2 or 3 sentences, describe a grumpy troll who LOVES the {present} it was just given, and happily lets the hero cross its bridge.")
say(story)
banner("You crossed the bridge!", "green")
