# scorekeeping-chatbot
A python-based chatbot for FB Messenger that tracks scores.  

## Installation

Download this directory. Install fbchat with pip. Add the email and password of a working facebook account to `login.py`, and clear the `uid_to_name.txt` and `name_to_score.txt` files. 

WARNING: This bot does not abide by the Facebook Terms and Conditions. If you spam a messenger chat using this bot, FB will likely mark your account as malicious and close it.

## Usage 

To run, type `python3 chatbot.py` into your terminal. (For long-term usage, I have mine set up to run constantly on a headless raspberry pi.) To see relevant commands, type `/help` in a Messenger chat with the bot's account. (This video is helpful for reference; it uses the same python module but adds in support for DialogFlow. https://youtu.be/hIcZZCnFcH4)

This bot is designed to be used in a FB Messenger group chat, but it can be used by separate individuals via private message due to the way the Scorekeeper class stores information in a text file.

## About the `Scorekeeper` class

The `Scorekeeper` class takes four arguments: the first two being the login credentials of the designated FB account and the next two being an initial list of people on the scoreboard and the word they will use to increment their own scores. It updates `uid_to_name.txt` every time someone new texts its linked account, and updates `name_to_score.txt` when a new name is added to its whitelist. 

## TO-DO:

- [ ] Create admin privileges – users who have the ability to modify the whitelist and scoreboard
- [ ] Devise a better method of data storage than local text files (Google Sheets, perhaps)
- [ ] Make `command_list.txt` based on actual commands used rather than hardcoding it
