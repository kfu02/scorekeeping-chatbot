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
        print("Initializing...")
        super().__init__(email, pwd)
        stored_dicts = self.readFromFiles()
        self.name_to_score = stored_dicts[0] #username: score
        self.uid_to_name = stored_dicts[1] #uid: username
        self.whitelist = whitelist #users who can change their score
        self.admins = admins #users with full access to all commands
        self.keyword = key #word to increment score
        #for user in whitelist:
        #    self.name_to_score[user] = 0
        self.supress_rand_strs = False
        self.updateUsers()

    def updateUsers(self):
        print('Updating users...')
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
        print('Writing to files...')
        print(self.name_to_score)
        print(self.uid_to_name)
        #writes all current data structures to files
        f = open('name_to_score.pkl', 'wb')
        pickle.dump(self.name_to_score, f)
        f.close()

        f = open('uid_to_name.pkl', 'wb')
        pickle.dump(self.uid_to_name, f)
        f.close()

    def readFromFiles(self):
        print("Reading from files...")
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
                #print(args)
                if len(args) == 4:
                    name = (' '.join(args[1:3])).title()
                    points = int(args[3])
                    return self.addToScoreboard(name, points)
            if msg_text == "quiet":
                self.supress_rand_strs = True
                return str(self.supress_rand_strs)
            if msg_text == "unquiet":
                self.supress_rand_strs = True
                return str(self.supress_rand_strs)

        return "Command not recognized. Typo?"

    def tallyScores(self):
        if self.name_to_score:
            #write current scores to file
            scores = ""
            for name, score in self.name_to_score.items():
                scores += name + ": " + str(score) + "\n"
            return scores
        return "Scoreboard empty."

    def addToScoreboard(self, name, amount):
        #add amount to author_id's score in scoreboard
        if name in self.whitelist:
            self.name_to_score[name] += amount
            return "Score updated.\n"+self.tallyScores()
        else:
            return "Not on scoreboard."

    def spitRandomWords(self, word_file, length):
        #returns string of words with random ending punc
        word_list = open(word_file, 'r').read().split('\n')[:-1]
        random.seed(time.time())
        output = [random.choice(word_list) for i in range(length)]
        return " ".join(output)+random.choice([".", "!", "?", ""])

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.updateUsers()
        #main looping function that checks for incoming messages and reacts
        self.markAsDelivered(thread_id, message_object.uid)
        time.sleep(random.randint(1,4)) #wait a few seconds before marking as read
        self.markAsRead(thread_id)

        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        #if bot not the author, reply
        if author_id != self.uid:
            time.sleep(random.randint(1,4)) #wait a few seconds before responding to command
            #self.updateUsers()
            try:
                msg_text = message_object.text.lower()
            except AttributeError: #emoji sent
                msg_text = ""

            time.sleep(random.randint(1,2)) #wait a couple seconds before replying

            if msg_text == self.keyword: #if keyword, add to score
                name = self.uid_to_name[author_id]
                reply = self.addToScoreboard(name, 1)
                print(msg_text, name, reply)
                self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)
                return

            #execute command, update text files
            if "/" in msg_text:
                reply = self.commandHandler(author_id, msg_text)
                print(self.name_to_score)
                print(self.uid_to_name)
                print(reply)
                self.send(Message(text=reply), thread_id=thread_id, thread_type=thread_type)

            if not self.supress_rand_strs: #always sends a rand msg
                self.send(Message(text=self.spitRandomWords("list_of_words.txt", random.randint(2, 10))), thread_id=thread_id, thread_type=thread_type)

if __name__ == '__main__':
    client = Scorekeeper(secret.email, secret.password, secret.WHITELIST, secret.ADMINS, secret.keyword)
    client.listen()
