"""
Helpers that make text adventures colorful and fun.

You don't need to read this file yet -- you just get to use it.
Everything here is pure standard library, so there's nothing to install.
"""

import json
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

# If you ever see junk on the screen like [0m or [92m,
# change this to False.
USE_COLOR = True

# How fast the words appear. Bigger = slower. 0 = instant.
SPEED = 0.02

# The model oracle() asks. Needs the Ollama app running (ollama.com) with
# this model pulled once: `ollama pull qwen3.5:4b`. For a faster (but sillier)
# oracle on an older computer, try "qwen3.5:2b".
ORACLE_MODEL = "qwen3.5:4b"
_OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
_OLLAMA_PULL_URL = "http://localhost:11434/api/pull"

# All the color names you can pass to paint() and write().
_CODES = {
    "red": "\033[91m",
    "orange": "\033[38;5;208m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "cyan": "\033[96m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "pink": "\033[38;5;213m",
    "brown": "\033[38;5;130m",
    "white": "\033[97m",
}
_RESET = "\033[0m"

# The list of color names above, so other files can check
# "is this a color I know about?" without poking at _CODES directly.
COLORS = list(_CODES)

# Matches any color code that paint()/write() can add, so we can strip
# them back out again (say() needs plain text, not color codes).
_COLOR_CODE_RE = re.compile(r"\033\[[0-9;]*m")

_SAVE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "finished_stories.txt"
)


def strip_color(text):
    """Get the plain version of some colorful text, with no color in it.

    Handy when you have text made with paint() (or a story built out of
    it) and you need a plain version instead -- say() does this for you
    automatically, so you'll rarely need to call this yourself.

    Args:
        text: Some text, possibly colored with paint().

    Returns:
        The same text, but with no color in it.
    """
    return _COLOR_CODE_RE.sub("", text)


def paint(text, color="white"):
    """Get a version of some text that shows up in a chosen color.

    Use this to color a single word or sentence before printing it, or
    to color part of a bigger story before passing the whole thing to
    write() or say().

    Args:
        text: The text to color.
        color: A color name, like "red", "pink", or "cyan". See COLORS
            for the full list.

    Returns:
        The colored text, ready to print() or pass to write() or say().
    """
    if not USE_COLOR:
        return text
    return _CODES.get(color, "") + text + _RESET


def write(text, color="white", speed=None):
    """Print text one letter at a time, like somebody typing it.

    Args:
        text: The text to print.
        color: What color to print it in.
        speed: How slowly to type, in seconds between letters. 0 prints
            it instantly instead. Defaults to SPEED.
    """
    text = text.strip()
    if speed is None:
        speed = SPEED
    if USE_COLOR:
        sys.stdout.write(_CODES.get(color, ""))
    for letter in text:
        sys.stdout.write(letter)
        sys.stdout.flush()
        if speed:
            time.sleep(speed)
    if USE_COLOR:
        sys.stdout.write(_RESET)
    print()


# An alias for write(), so say() can still use it even though say() has
# its own parameter named "write".
_type_out = write

_SPEECH_CMD = shutil.which("say")  # macOS's built-in text-to-speech


def say(text, voice=None, write=True, color="white", speed=None):
    """Have the computer read text out loud.

    By default this also types the text out on screen at the same time
    it's being spoken, so players can follow along even without sound.
    If the text was colored with paint(), those colors show up in the
    typed version too -- only the spoken version drops the colors,
    since there's no such thing as a pink voice.

    Args:
        text: The text to speak (and, by default, to type out).
        voice: An optional voice to use instead of the default. On a
            Mac, try running `say -v ?` in a terminal to see the list.
        write: If True (the default), types the text out on screen at
            the same time it's being spoken. Set this to False to speak
            silently, with nothing shown on screen.
        color: What color to type the text in, if write=True.
        speed: How slowly to type, if write=True. See write() for what
            this means.

    Note:
        Speech only works on some computers. If yours can't talk, this
        just shows a short message instead (and still types out the
        text if write=True).
    """
    spoken = strip_color(text).strip()
    if not _SPEECH_CMD:
        if write:
            _type_out(text, color, speed)
        write_notice = "(no text-to-speech found on this computer)"
        _type_out(write_notice, "red", speed=0)
        return
    cmd = [_SPEECH_CMD]
    if voice:
        cmd += ["-v", voice]
    cmd.append(spoken)
    if write:
        # Start the speech in the background (instead of waiting for it
        # to finish) so we can type the text out on screen at the same
        # time, then wait for the speech to catch up before moving on.
        speech = subprocess.Popen(cmd)
        _type_out(text, color, speed)
        speech.wait()
    else:
        subprocess.run(cmd, check=False)


def dice(sides=6):
    """Roll a die with this many sides and return the number that lands.

    Args:
        sides: How many sides the die has, e.g. 6 for a normal die.

    Returns:
        A random whole number from 1 to sides, inclusive.
    """
    return random.randint(1, sides)


# Fun things to show on screen while the oracle is busy, so players can
# tell it's working hard (and not just frozen). Add your own!
_THINKING_MESSAGES = [
    "The oracle is thinking",
    "The oracle is gazing into its crystal ball",
    "The oracle is consulting the stars",
    "The oracle is stroking its long beard",
    "The oracle is asking its pet owl",
    "The oracle is flipping through dusty old books",
]
_WRITING_MESSAGES = [
    "The oracle is writing",
    "The oracle is dipping its quill in ink",
    "The oracle is scribbling furiously",
]


class _ThinkingDots:
    """Shows an animated "The oracle is thinking . . ." line while it works.

    Runs in the background so the dots keep moving while we wait for the
    model. Call writing() once the model starts writing its answer, and
    stop() when it's done to erase the line again.
    """

    def __init__(self):
        self._messages = _THINKING_MESSAGES
        self._done = threading.Event()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def writing(self):
        self._messages = _WRITING_MESSAGES

    def stop(self):
        self._done.set()
        self._thread.join()

    def _animate(self):
        width = 0
        tick = 0
        messages = None
        while not self._done.is_set():
            # Pick a new message every few seconds, or right away if we
            # just switched from thinking to writing.
            if self._messages is not messages or tick % 8 == 0:
                messages = self._messages
                message = messages[0] if tick == 0 else random.choice(messages)
            line = message + " ." * (tick % 4 + 1)
            sys.stdout.write("\r" + paint(line.ljust(width), "purple"))
            sys.stdout.flush()
            width = max(width, len(line))
            tick += 1
            self._done.wait(0.4)
        sys.stdout.write("\r" + " " * width + "\r")
        sys.stdout.flush()


def _oracle_stream(prompt, system, temperature, think, dots, think_budget=0):
    """Send one prompt to Ollama and collect its thinking and its answer.

    Args:
        prompt, system, temperature: See _oracle_generate().
        think: Whether the model should think before answering.
        dots: The _ThinkingDots on screen, told when writing starts.
        think_budget: If thinking, stop listening after about this many
            word pieces of thinking (small models can ramble for ages).

    Returns:
        A pair (thinking, answer). The answer is "" if the model was cut
        off before it finished thinking.
    """
    body = json.dumps(
        {
            "model": ORACLE_MODEL,
            "system": system,
            "prompt": prompt,
            # Stream the reply bit by bit, so we can watch how long the
            # model has been thinking and see when it starts writing.
            "stream": True,
            "think": think,
            "options": {
                "temperature": temperature,
                # These two keep the randomness sensible: the model only
                # picks among its more likely next words.
                "top_p": 0.95,
                "top_k": 20,
            },
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        _OLLAMA_GENERATE_URL, data=body, headers={"Content-Type": "application/json"}
    )
    thinking = ""
    answer = ""
    pieces = 0
    with urllib.request.urlopen(request, timeout=120) as response:
        for raw_line in response:
            if not raw_line.strip():
                continue
            chunk = json.loads(raw_line)
            if chunk.get("error"):
                raise RuntimeError(f"The oracle had a problem: {chunk['error']}")
            if chunk.get("thinking"):
                thinking += chunk["thinking"]
                pieces += 1
                if pieces > think_budget:
                    break  # Hanging up tells Ollama to stop, too.
            if chunk.get("response"):
                if not answer:
                    dots.writing()
                answer += chunk["response"]
    return thinking, answer


def _oracle_generate(prompt, system, temperature, think_budget):
    """Ask ORACLE_MODEL something and return its answer.

    While waiting, shows the animated "The oracle is thinking..." line.

    Args:
        prompt: The text prompt to send to ORACLE_MODEL.
        system: Instructions for how the model should behave.
        temperature: How random/creative the reply should be. 0 always
            gives the same, most-likely answer; higher values (up to
            about 1) make the model take more chances.
        think_budget: How long the model may think before answering,
            in word pieces (about 30 per second on a laptop). 0 means
            answer right away without thinking. If it runs out mid-
            thought, it answers from the notes it has so far.

    Returns:
        The model's answer (without its thinking), as a plain string.
    """
    dots = _ThinkingDots()
    try:
        thinking, answer = _oracle_stream(
            prompt, system, temperature, think_budget > 0, dots, think_budget
        )
        if not answer:
            # Out of thinking time: hand the model its notes and ask it
            # to answer right now.
            prompt += (
                "\n\nYour notes from thinking it over:\n"
                f"{thinking.strip()}\n\n"
                "That's enough thinking -- give your final reply now."
            )
            _, answer = _oracle_stream(prompt, system, temperature, False, dots)
    finally:
        dots.stop()
    return answer


def _oracle_install():
    """Download ORACLE_MODEL, printing a live progress line as it goes.

    Called automatically by oracle() the first time it can't find the
    model already installed.
    """
    print()
    print(paint(f"The oracle needs to download its brain ({ORACLE_MODEL})...", "yellow"))
    body = json.dumps({"model": ORACLE_MODEL, "stream": True}).encode("utf-8")
    request = urllib.request.Request(
        _OLLAMA_PULL_URL, data=body, headers={"Content-Type": "application/json"}
    )
    last_line = ""
    with urllib.request.urlopen(request, timeout=600) as response:
        for raw_line in response:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            update = json.loads(raw_line)
            if update.get("error"):
                raise RuntimeError(
                    f"Couldn't download {ORACLE_MODEL}: {update['error']}"
                )
            total = update.get("total")
            done = update.get("completed")
            if total and done is not None:
                line = f"  {done * 100 // total}% downloaded"
            else:
                line = "  " + update.get("status", "")
            if line != last_line:
                sys.stdout.write("\r" + paint(line.ljust(30), "yellow"))
                sys.stdout.flush()
                last_line = line
    print()
    print(paint("Done! The oracle is ready.", "green"))
    print()


def _oracle_call(prompt, system, temperature, think_budget=0):
    """Send a prompt to the oracle model, installing it first if needed.

    This is the part oracle() and imagine() share: talk to Ollama, and if
    the model isn't downloaded yet, download it and try again.

    Args:
        prompt, system, temperature, think_budget: Passed along to
            _oracle_generate() -- see there for what they mean.

    Returns:
        The model's answer, as a plain string.

    Raises:
        RuntimeError: If Ollama isn't running or the model can't be
            reached for some other reason.
    """
    args = (prompt, system, temperature, think_budget)
    try:
        return _oracle_generate(*args)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise RuntimeError(
                f"The oracle had a problem ({error.code}). Is "
                f"{ORACLE_MODEL!r} a real model name?"
            )
        _oracle_install()
        return _oracle_generate(*args)
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError(
            "Couldn't reach the oracle. Is the Ollama app running?"
        )


def oracle(question, temperature=0.6):
    """Ask a small AI a yes-or-no question and get its answer.

    Use this whenever your story needs to decide something and you want
    an AI to be the judge -- like whether an item counts as a weapon, or
    whether the player's answer makes sense.

    While it works, it shows "The oracle is thinking . . ." on screen,
    so players know it's busy. The first time you call this, your computer may
    take a little longer to get the AI ready. If the oracle can't answer
    for some reason, it announces that it isn't feeling well and just
    flips a coin instead, so your story can keep going either way.

    Args:
        question: A yes-or-no question, written as a plain sentence,
            like "Is a pillow a good weapon against a dragon?".
        temperature: How much the oracle's mood can change from one ask
            to the next, from 0 (always the same answer) to 1 (more
            surprising). The default of 0.6 means it usually agrees with
            itself, but close calls can go either way.

    Returns:
        True or False, depending on what the AI decided (or, once in a
        while, what the coin flip decided).
    """
    system = (
        "You are the wise, playful oracle in a text adventure game made "
        "by and for kids. Players ask you yes-or-no questions about "
        "what happens in the story. Judge them the way a fair, "
        "imaginative game master would: use common sense about the "
        "real world, but play along with the fantasy of the story "
        "(dragons, magic, and talking animals are real here). Reply "
        "with exactly one word: true or false."
    )
    try:
        reply = _oracle_call(
            f"Question: {question}", system, temperature
        )
        match = re.search(r"\b(true|false|yes|no)\b", reply, re.IGNORECASE)
        if not match:
            raise RuntimeError(f"The oracle gave a weird answer: {reply!r}")
        return match.group().lower() in ("true", "yes")
    except RuntimeError:
        write("The oracle is not feeling well today...", "yellow")
        return random.choice([True, False])


def imagine(prompt, temperature=0.7):
    """Ask a small AI to write something creative for your story.

    Use this whenever you want part of your story written for you
    instead of writing it yourself -- a description, a scene, a poem, a
    joke, whatever you ask for. It writes in English for a
    middle-school aged audience, and tries to be funny.

    While it works, it shows "The oracle is thinking . . ." on screen,
    so players know it's busy. Ask for the same thing twice and you'll
    get something different each time.

    Args:
        prompt: What you want written, like "a poem about a dragon who
            is afraid of toast" or "a short scene where two robots meet
            for the first time".
        temperature: How wild and unexpected the writing should be, from
            0 (plainer, safer) to about 1 (more surprising, but more
            likely to stop making sense). The default of 0.7 is usually
            a good middle ground.

    Returns:
        The written text, as a plain string, ready to print, speak, or
        drop into the rest of your story.

    Raises:
        RuntimeError: If the AI couldn't be reached. See the README for
            setup help.
    """
    system = (
        "You are the storyteller for a text adventure game played by "
        "kids around 10 to 13. Write exactly what is asked, and stay "
        "true to the scene you're given -- don't add random new "
        "things. Be funny in a clever, playful way: one good joke beats "
        "lots of nonsense. Use clear, simple sentences and concrete "
        "details. Keep it gentle -- silly, not scary or violent. Keep it "
        "short unless asked for more. Reply with only the writing "
        "itself, with no title or notes."
    )
    return _oracle_call(prompt, system, temperature).strip()


def ask(question, color="cyan", allow_empty=False):
    """Ask a question and wait for the player to type an answer.

    Args:
        question: The prompt to show the player.
        color: What color to show the prompt in.
        allow_empty: If False (the default), keeps asking until the
            player types something. If True, an empty answer is okay.

    Returns:
        Whatever the player typed, with extra spaces trimmed off.
    """
    while True:
        answer = input(paint(question, color)).strip()
        if answer or allow_empty:
            return answer
        write("You have to type something!", "red", speed=0)


def banner(title, color="yellow"):
    """Print a title inside a box of stars.

    Args:
        title: The text to show. It gets shown in ALL CAPS.
        color: What color to print the box and title in.
    """
    line = "*" * (len(title) + 8)
    print()
    print(paint(line, color))
    print(paint("*** " + title.upper() + " ***", color))
    print(paint(line, color))
    print()


def drumroll(dots=3):
    """Dot dot dot, for suspense.

    Args:
        dots: How many dots to print, with a little pause between each.
    """
    for _ in range(dots):
        sys.stdout.write(paint(" .", "yellow"))
        sys.stdout.flush()
        time.sleep(0.4)
    print()


def clear():
    """Wipe the screen clean, like starting on a fresh page."""
    if USE_COLOR:
        print("\033[2J\033[H", end="")
    else:
        print("\n" * 30)


def save_story(title, text):
    """Add a finished story to finished_stories.txt so we can keep it.

    Args:
        title: A short name for this story, used as a heading.
        text: The full story text to save.
    """
    with open(_SAVE_FILE, "a") as f:
        f.write("=== " + title + " ===\n")
        f.write(text.strip() + "\n\n")
