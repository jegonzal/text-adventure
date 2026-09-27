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
import time
import urllib.error
import urllib.request

# If you ever see junk on the screen like [0m or [92m,
# change this to False.
USE_COLOR = True

# How fast the words appear. Bigger = slower. 0 = instant.
SPEED = 0.02

# The model oracle() asks. Needs the Ollama app running (ollama.com) with
# this model pulled once: `ollama pull qwen3.5:2b`
ORACLE_MODEL = "qwen3.5:2b"
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

_SAVE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "finished_stories.txt"
)


def paint(text, color="white"):
    """Wrap some text in a color.

    Args:
        text: The text to color.
        color: One of the names in _CODES, like "red" or "green".

    Returns:
        The same text, surrounded by the color codes that make a
        terminal print it in that color (or the plain text, unchanged,
        if USE_COLOR is False).
    """
    if not USE_COLOR:
        return text
    return _CODES.get(color, "") + text + _RESET


def write(text, color="white", speed=None):
    """Print text one letter at a time, like somebody typing it.

    Args:
        text: The text to print.
        color: What color to print it in.
        speed: Seconds to pause between letters. 0 means print instantly.
            Defaults to SPEED.
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


_SPEECH_CMD = shutil.which("say")  # macOS's built-in text-to-speech


def say(text, voice=None):
    """Have the computer read text out loud.

    Args:
        text: The text to speak.
        voice: An optional voice name to use instead of the default
            (macOS only -- run `say -v ?` in a terminal to see the list).

    Note:
        This only works on macOS, since it uses the built-in `say`
        command. On other computers it just prints a message instead.
    """
    text = text.strip()
    if not _SPEECH_CMD:
        write("(no text-to-speech found on this computer)", "red", speed=0)
        return
    cmd = [_SPEECH_CMD]
    if voice:
        cmd += ["-v", voice]
    cmd.append(text)
    subprocess.run(cmd, check=False)


def dice(sides=6):
    """Roll a die with this many sides and return the number that lands.

    Args:
        sides: How many sides the die has, e.g. 6 for a normal die.

    Returns:
        A random whole number from 1 to sides, inclusive.
    """
    return random.randint(1, sides)


def _oracle_generate(prompt):
    """Send one prompt to Ollama and return the model's raw reply text.

    Args:
        prompt: The full text prompt to send to ORACLE_MODEL.

    Returns:
        The model's reply, as a plain string.
    """
    body = json.dumps(
        {
            "model": ORACLE_MODEL,
            "prompt": prompt,
            "stream": False,
            # Reasoning models like this one "think" before answering by
            # default, which is slow and pointless for a one-word answer.
            "think": False,
            "options": {"temperature": 0},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        _OLLAMA_GENERATE_URL, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())["response"]


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


def oracle(question):
    """Ask a small local AI to answer a yes-or-no question.

    Needs the Ollama app running (ollama.com); the model gets downloaded
    automatically the first time you use this if it isn't already.

    Args:
        question: The yes-or-no question to ask, as a plain sentence.

    Returns:
        True or False, depending on what the AI decided.

    Raises:
        RuntimeError: If Ollama isn't running, or the model gave back
            something that wasn't a clear yes or no.
    """
    prompt = (
        "You are a yes-or-no oracle. Answer with exactly one word: "
        'either "true" or "false". Do not explain. Do not say anything '
        "else.\n\n"
        f"Question: {question}\n"
        "Answer:"
    )
    try:
        reply = _oracle_generate(prompt)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise RuntimeError(
                f"The oracle had a problem ({error.code}). Is "
                f"{ORACLE_MODEL!r} a real model name?"
            )
        _oracle_install()
        reply = _oracle_generate(prompt)
    except urllib.error.URLError:
        raise RuntimeError(
            "Couldn't reach the oracle. Is the Ollama app running?"
        )

    match = re.search(r"\btrue\b|\bfalse\b", reply, re.IGNORECASE)
    if not match:
        raise RuntimeError(f"The oracle gave a weird answer: {reply!r}")
    return match.group().lower() == "true"


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
