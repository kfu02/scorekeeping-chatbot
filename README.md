# scorekeeping-chatbot
A python-based chatbot for FB Messenger that tracks scores.  

## Installation

Download this directory. Install fbchat with pip. Add the email and password of a working facebook account to `secret.py`. Also add lists of names called WHITELIST and ADMINS to `secret.py`. Finally, add a keyword variable to the `secret.py` file: this will be the trigger to increment a user's score.
(If login fails, try logging in on https://m.facebook.com/login.php by hand, then calling chatbot.py.)

WARNING: This bot does not abide by the Facebook Terms and Conditions. If you spam a messenger chat using this bot, FB will likely mark your account as malicious and close it.

## Usage

To run, type `python3 chatbot.py` into your terminal. (For long-term usage, I have mine set up to run constantly on a headless raspberry pi.) To see a list of commands, type `/help` in a Messenger chat with the bot's account. (This video is helpful for reference; it uses the same python module but adds in support for DialogFlow. https://youtu.be/hIcZZCnFcH4)

This bot is designed to be used in a FB Messenger group chat, but it can be used by separate individuals via private message.

## The `Scorekeeper` class

The `Scorekeeper` class takes four arguments: the first two being the login credentials of the designated FB account and the next two being an initial list of people on the scoreboard and the word they will use to increment their own scores. It updates `uid_to_name.pkl` every time someone new messages its linked account, and updates `name_to_score.pkl` when a new name is added to its whitelist.

## TO-DO:

- [ ] Update README properly.
- [ ] Streamline code.
- [ ] Remove deprecated files.
- [ ] Make `command_list.txt` based on actual commands used rather than hardcoding it
