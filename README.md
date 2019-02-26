# scorekeeping-chatbot
A python-based chatbot for FB Messenger that tracks scores.  

## Setup

Download this directory. Install fbchat with pip. Create a `secret.py` file with this format:

```python
#email and password of a working FB account
email =
password =
#names of users with full access to commands
ADMINS =
#names of users on the scoreboard
WHITELIST =
#word or phrase that will increment score
keyword =
```

WARNING: This bot does not abide by the Facebook Terms and Conditions. If you spam a messenger chat using this bot, FB will likely mark your account as malicious and close it. (The randomized reply delay and gibberish replies in chatbot.py are designed to combat this issue.)

## Usage

To run, type `python3 chatbot.py` into your terminal. (For long-term usage, I have mine set up to run constantly on a headless raspberry pi.) To see a list of commands, type `/help` in a Messenger chat with the bot's account. (This video is helpful for reference; it uses the same python module but adds in support for DialogFlow. https://youtu.be/hIcZZCnFcH4)

(If login fails on the first run, log in on https://m.facebook.com/login.php by hand, then call chatbot.py.)

This bot is designed to be used in a FB Messenger group chat, but it can be used by separate individuals via private message.

## TO-DO:

- [ ] Update README properly.
- [ ] Make bot better at updating list of users.
- [ ] Streamline code.
- [ ] Make `command_list.txt` based on actual commands used rather than hardcoding it
