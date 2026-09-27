# A tiny scratchpad for trying out the oracle() function by itself --
# ask it any yes-or-no question and see what it says.

from fun import *

question = ask("Ask me a yes no question: ")
if oracle(question):
    say("Yes")
else:
    say("No")
