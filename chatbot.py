"""https://fbchat.readthedocs.io/en/master/examples.html#examples"""

from fbchat import log, Client
from fbchat.models import *
import login

# Subclass fbchat.Client and override required methods
class Scorekeeper(Client):
    def __init__(self, email, pwd, whitelist, key):
        super().__init__(email, pwd)
        print("Reading from files...")
        stored_dicts = self.readFromFiles()
        self.name_to_score = stored_dicts[0] #username: score
        self.uid_to_name = stored_dicts[1] #uid: username
        self.whitelist = whitelist #users who can change their score
        self.keyword = key #word to increment score
        print("Done.")
        self.updateUsers()

    def updateUsers(self):
        #updates users that chatbot recognizes
        users = self.fetchAllUsers()
        for user in users:
            if user.uid not in self.uid_to_name:
                self.uid_to_name[user.uid] = user.name
        for name in self.uid_to_name.values():
            if name not in self.whitelist:
                try:
                    del self.name_to_score[name]
                except KeyError:
                    continue
            if name not in self.name_to_score and name in self.whitelist:
                self.name_to_score[name] = 0
        self.writeToFiles()

    def writeToFiles(self):
        #writes all current data structures to files
        with open("name_to_score.txt", 'w') as f:
            for name, score in self.name_to_score.items():
                f.write(name + " " + str(score) + "\n")
        f.close()
        with open("uid_to_name.txt", 'w') as f:
            for uid, name in self.uid_to_name.items():
                f.write(uid + " " + name + "\n")
        f.close()

    def readFromFiles(self):
        #takes input from score and uid files
        try:
            raw_name_to_score = open("name_to_score.txt", 'r').read().split("\n")[:-1]
            name_to_score = {}
            for line in raw_name_to_score:
                tokens = line.split(" ")
                name = tokens[0] + " " + tokens[1]
                score = int(tokens[2])
                name_to_score[name] = score

            raw_uid_to_name = open("uid_to_name.txt", 'r').read().split("\n")[:-1]
            uid_to_name = {}
            for line in raw_uid_to_name:
                tokens = line.split(" ")
                uid = tokens[0]
                name = tokens[1] + " " + tokens[2]
                uid_to_name[uid] = name
            return (name_to_score, uid_to_name)
        except FileNotFoundError:
            return ({},{})

    def commandHandler(self, author_id, msg_text):
        msg_text = msg_text[1:] #remove '/'

        if msg_text == "help": #displays commands & functions
            return open("command_list.txt", 'r').read()
        #UI commands
        if msg_text == "score":
            return self.tallyScores()
        if msg_text == "clear":
            for name in self.name_to_score:
                self.name_to_score[name] = 0
            return "Scores cleared.\n" + self.tallyScores()

        #admin commands
        if msg_text == "whitelist":
            return str(self.whitelist)
        if "mod" in msg_text:
            args = msg_text.split(" ")
            if args[0] == "mod":
                name = ' '.join(args[1:]).title()
                self.whitelist.append(name)
                self.writeToFiles()
                return str(self.whitelist)
            if args[0] == "unmod":
                name = ' '.join(args[1:]).title()
                if name in self.whitelist:
                    self.whitelist.remove(name)
                self.writeToFiles()
                return str(self.whitelist)

        return "Command not recognized. Typo?"

    def tallyScores(self):
        #write current scores to file
        scores = ""
        for name, score in self.name_to_score.items():
            scores += name + ": " + str(score) + "\n"
        self.writeToFiles()
        return scores

    def addToScoreboard(self, author_id):
        if author_id in self.uid_to_name:
            name = self.uid_to_name[author_id]
            print(name)
            print(self.whitelist)
            if name in self.whitelist:
                self.name_to_score[name] += 1
                return "Score updated.\n"+self.tallyScores()
            else:
                return "Not on scoreboard."
        return "???" #shouldn't be possible to get here

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        #main looping function that checks for incoming messages and reacts
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        # If you're not the author, echo
        if author_id != self.uid:
            self.updateUsers()
            try:
                msg_text = message_object.text.lower()
            except AttributeError: #emoji sent
                msg_text = ""

            if msg_text == self.keyword: #add to score
                reply = self.addToScoreboard(author_id)
                self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)
                return

            if "/" not in msg_text: #if not a command,
                return #ignore
            #else, execute command, update text files
            reply = self.commandHandler(author_id, msg_text)
            print(self.name_to_score)
            print(self.uid_to_name)
            print(reply)
            self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)

WHITELIST = [] #add names here
client = Scorekeeper(login.email, login.password, WHITELIST, "I scored!")
client.listen()
