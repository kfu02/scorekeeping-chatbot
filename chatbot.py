"""https://fbchat.readthedocs.io/en/master/examples.html#examples"""

from fbchat import log, Client
from fbchat.models import *
import secret
import time
import random
import pickle

# Subclass fbchat.Client and override required methods
class Scorekeeper(Client):
    def __init__(self, email, pwd, whitelist, admins, key):
        super().__init__(email, pwd)
        print("Reading from files...")
        stored_dicts = self.readFromFiles()
        self.name_to_score = stored_dicts[0] #username: score
        self.uid_to_name = stored_dicts[1] #uid: username
        self.whitelist = whitelist #users who can change their score
        self.admins = admins #users with full access to all commands
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
        f = open('name_to_score.pkl', 'wb')
        pickle.dump(self.name_to_score, f)
        f.close()

        f = open('uid_to_name.pkl', 'wb')
        pickle.dump(self.uid_to_name, f)
        f.close()
        """
        with open("name_to_score.txt", 'w') as f:
            for name, score in self.name_to_score.items():
                f.write(name + " " + str(score) + "\n")
        f.close()
        with open("uid_to_name.txt", 'w') as f:
            for uid, name in self.uid_to_name.items():
                f.write(uid + " " + name + "\n")
        f.close()
        """

    def readFromFiles(self):
        #takes input from score and uid files
        try:
            f = open('name_to_score.pkl', 'rb')
            ns = pickle.load(f)
            f.close()

            f = open('uid_to_name.pkl', 'rb')
            un = pickle.load(f)
            f.close()
            print(ns)
            print(un)
            return (ns, un)
        except FileNotFoundError:
            return ({}, {})
        """
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
        """

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
        if self.uid_to_name[author_id] in self.admins:
            if msg_text == "whitelist":
                return str(self.whitelist)
            if msg_text == "admins":
                return str(self.admins)
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
            if "add" in msg_text:
                args = msg_text.split(" ")
                if len(args) == 4:
                    name = (' '.join(args[1:3])).title()
                    points = int(args[3])
                    uid = -1
                    for u, n in self.uid_to_name.items(): #find uid of name given
                        if n == name:
                            uid = u
                    if uid != -1:
                        self.addToScoreboard(uid, points)
                        return self.tallyScores()

        return "Command not recognized. Typo?"

    def tallyScores(self):
        #write current scores to file
        scores = ""
        for name, score in self.name_to_score.items():
            scores += name + ": " + str(score) + "\n"
        self.writeToFiles()
        return scores

    def addToScoreboard(self, author_id, amount):
        #add amount to author_id's score in scoreboard
        if author_id in self.uid_to_name:
            name = self.uid_to_name[author_id]
            if name in self.whitelist:
                self.name_to_score[name] += amount
                return "Score updated.\n"+self.tallyScores()
            else:
                return "Not on scoreboard."
        return "???" #shouldn't be possible to get here

    def spitRandomWords(self, word_file, length):
        #returns string of words with random ending punc
        word_list = open(word_file, 'r').read().split('\n')[:-1]
        random.seed(time.time())
        output = [random.choice(word_list) for i in range(length)]
        return " ".join(output)+random.choice([".", "!", "?", ""])

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        #main looping function that checks for incoming messages and reacts
        self.markAsDelivered(thread_id, message_object.uid)
        time.sleep(random.randint(3,5)) #wait a few seconds before marking as read
        self.markAsRead(thread_id)

        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        #if bot not the author, reply
        if author_id != self.uid:
            self.updateUsers()
            try:
                msg_text = message_object.text.lower()
            except AttributeError: #emoji sent
                msg_text = ""

            time.sleep(random.randint(1,2)) #wait a couple seconds before replying

            if msg_text == self.keyword: #if keyword, add to score
                reply = self.addToScoreboard(author_id, 1)
                self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)
                return

            #execute command, update text files
            if "/" in msg_text:
                reply = self.commandHandler(author_id, msg_text)
                print(self.name_to_score)
                print(self.uid_to_name)
                print(reply)
                self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)

            if random.random()<0.20: #every 5th message reply something random
                self.send(Message(text=self.spitRandomWords("list_of_words.txt", random.randint(2, 10))), thread_id=thread_id, thread_type=thread_type)

if __name__ == '__main__':
    client = Scorekeeper(secret.email, secret.password, secret.WHITELIST, secret.ADMINS, secret.keyword)
    client.listen()
