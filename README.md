# Text Adventure

A tiny, kid-friendly toolkit for writing your own text adventures and
fill-in-the-blanks stories in Python. No libraries to install -- just
Python and your imagination.

## What's in here

- **[fun.py](fun.py)** -- the toolbox. Functions for colorful text, typewriter
  printing, text-to-speech, dice rolls, asking the player questions, and
  even a little AI "oracle" that can answer yes-or-no questions. You
  don't need to understand this file to use it, but it's worth a read
  once you're curious how it works.
- **[story.py](story.py)** -- a fill-in-the-blanks story. It asks you for some
  words (a color, a name, an animal...) and drops them into a story.
- **[game.py](game.py)** -- a choose-your-own-weapon dragon adventure.
- **[play.py](play.py)** -- a tiny scratchpad for asking the oracle any
  yes-or-no question.

## Getting started

You just need Python 3 installed. Then run any of the story files, for
example:

```
python3 story.py
```

Answer the questions it asks, and watch your story get written!

### Optional extras

- **Text-to-speech**: on a Mac, stories will automatically be read out
  loud using the built-in `say` command. On other computers this step
  is skipped.
- **The oracle**: `game.py` and `play.py` use a function called `oracle()`
  that asks a small AI a yes-or-no question. This needs
  [Ollama](https://ollama.com) installed and running on your computer.
  The first time you use it, it will download the small model it needs
  automatically.

## Make your own

The best way to learn is to open up `story.py` or `game.py` and start
changing things:

- Change the questions it asks.
- Change the story template to make your own plot.
- Add a new `ask()` for another word and use it in the story.
- Try adding a new file of your own that uses the functions in `fun.py`!

Have fun, and see what kind of wild stories you can build.
