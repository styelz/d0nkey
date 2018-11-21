import os
import re
import sys
import random
import socket
import string
import importlib
import ast
import atexit
import threading
import traceback
import errno
import numpy as np
import fnmatch
from random import *
from time import sleep
from time import time
from datetime import datetime
bot = None

def main():    
        bot = PluginBot()
        bot.connect()        
        bot.run()
        

def BYTE(message):
    return bytes("%s\r\n" % message, "UTF-8")

def getUser(token):
    user = token[0].strip(":")
    user = user.split("!")
    return user

def getMessage(line):
    line=line.split(" ")
    msg=""
    cnt=0
    while (cnt < len(line)):
        if (cnt>2): msg+=("%s " % line[cnt])
        cnt+=1
    return msg.strip()



class PluginBot(threading.Thread):
    userInput = None
    s = None
    loadedModules = dict()
    isRunning = False
    guiParent = None
    realName = "d0nkey"
    password = "a1b2c3d4"
    nickName = "d0nkey"
    host = "irc.dlnetworks.net"
    port = (6667)
    master = ["reflector","pbp"]
    weConnected = False
    joined = False
    channels = {}
    scores = {}
    scores_tmp = {}
    quotes = {}
    shout = {}               
    ripnick = ""
    lastrollnick = ""
    udice=["0","\u2680","\u2681","\u2682","\u2683","\u2684","\u2685"]
    dscores={5:13,6:12,7:11,8:10,9:9,10:8,11:7,12:6,13:5,14:4,15:3,16:2,17:1,18:1,19:2,20:3,21:4,22:5,23:6,24:7,25:8,26:9,27:10,28:11,29:12,30:13}
    nickhost = []
    lastmsg=""
    dsmp=2


    def connect(self):
        
        if (self.s == None):
            self.s = socket.socket()
            print("Connecting to host \"%s\" with port %d." % (self.host, self.port))

        tries=0
        while (True):
            try:
                self.s.connect((self.host, self.port))
                break
            except Exception as e:
                tries+=1
                if (tries==4): 
                    print("Too many retries, giving up")
                    sys.exit()
                print("Timeout error. Retying [%s of 3]" % tries)
                sleep(2)
            
        sleep(0.5)
        
        print("Setting mode for %s" % (self.realName))
        self.s.send(BYTE("USER %s %s unused :%s" % (self.password, self.host, self.realName)))
        sleep(0.5)

        
        print("Logging in using nickname.")
        self.s.send(BYTE("NICK %s" % self.nickName))
        sleep(0.5)
                            
        self.weConnected = True
        
           
    def run(self):
        self.isRunning = True
        readBuffer = ""

        self.loadDataFiles(False)
        
        sys.stdout = open(sys.stdout.buffer.fileno(), 'w', encoding='utf8')

        while (self.isRunning):
            try:
                if (self.s != None):
                    try:
                        temp = self.s.recv(1024).decode("UTF-8")
                    except Exception:
                        temp = ""
                        continue
                    sys.stdout.buffer.write(temp.encode('utf8'))
                    if (temp == ""):
                        self.isRunning = False
                    else:
                        readBuffer += temp
                        temp = readBuffer.split("\n")
                        readBuffer = temp.pop()

                        # 
                        # Respond to certain server messages
                        #

                        for line in temp:
                            tokens=self.makeTokens(line)
                            self.join(tokens)
                            self.kicked_rejoin(tokens)
                            self.loadDataFiles(tokens)
                            self.ping(tokens)
                            self.say(tokens,line)
                            self.dice(tokens,line)
                            self.dice_scores(tokens)
                            self.dice_record(tokens)
                            self.quoteman(tokens,line)
                            self.chanman(tokens)
                            self.userman(tokens,line)
                            self.rip(tokens)
                            self.fish_slap(tokens)
                            self.help(tokens)
                            self.chuck(tokens,line)
                            self.shouts(tokens,line)

            except Exception:
                traceback.print_tb(sys.exc_info()[2])
                sys.exit()
                
    def join(self,tokens):
        if (self.joined == True): return
        if (tokens[1] == "MODE"):
            self.joined = True
            self.s.send(BYTE(":%s PRIVMSG %s :IDENTIFY %s" % (self.nickName,"nickserv",self.password)))
            if (len(self.channels)>0):
                for channel, v in self.channels.items():
                    self.s.send(BYTE("JOIN %s" % channel))

    def kicked_rejoin(self,tokens):
        if (tokens[1] == "KICK"):
            if (tokens[3] == self.nickName):
                self.s.send(BYTE("JOIN %s" % tokens[2]))

    def ping(self, tokens):
        if (tokens[0] == "PING"):
            currentDate = datetime.now()
            print("[%02s:%02s] Received PING PONG" % (str(currentDate.hour).zfill(2), str(currentDate.minute).zfill(2)), end = "\r")
            str1 = ("PONG %s" % tokens[1].strip(":"))
            self.s.send(BYTE(str1))        

    def help(self,tokens):
      try:
        if (tokens[1] == "PRIVMSG"):
            if not (self.pubCheck(tokens)): return
            if (tokens[3] == ".help"):
                help=[]
                help.append("* Help/Commands:")
                help.append("* Type each command for extra help")
                help.append("* .dice    Dice Game")
                help.append("* .say     Make the bot say something")
                help.append("* .quote   Show/Manage Quotes")
                help.append("* .rip     R.I.P for last quit/part nick")
                #help.append("* .chan    Channel Manager")
                for line in help:
                    self.s.send(BYTE(":%s NOTICE %s :%s" % (self.nickName,tokens[0],line)))
                    sleep(1)
      except:
        derp=0

    def say(self, tokens, line):
        try:
            if (tokens[1] == "PRIVMSG"):
                if not (self.pubCheck(tokens)):
                    if (tokens[3] == ".say"):
                        if (tokens[4] in self.channels or tokens[4] == "nickserv"):
                            if (len(tokens) > 5):
                                if (tokens[4]==".roll"):
                                    if (len(tokens) > 6): rollGuess=int(tokens[6])
                                    tokens=[self.nickName, 'PRIVMSG', tokens[2], '.roll', rollGuess]
                                    self.dice(tokens,line)
                                    return
                                else:
                                    msg=getMessage(line).replace(":.say %s " % tokens[4],"")
                                    self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[4],msg)))
                elif (tokens[3] == ".say"):
                    if (len(tokens) > 4):
                        if (tokens[4]==".roll"):
                            if (len(tokens) > 5): rollGuess=int(tokens[5])
                            else: rollGuess=randint(5,30)
                            tokens=[self.nickName, 'PRIVMSG', tokens[2], '.roll', rollGuess]
                            self.dice(tokens,line)
                            return
                        else:
                            msg=getMessage(line).replace(":.say ","")
                    else:
                        msg="Usage: .say <something>"
                    self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))
        except:
            derp=0

    def dice(self, tokens, line):
      try:
        if (tokens[1] == "PRIVMSG"):
            pm=0;
            replyTo=tokens[2]
            if not (self.pubCheck(tokens)):
                pm=1;
                replyTo=tokens[0];

            if (len(tokens)>4):
                if (tokens[4]=="score" or tokens[4]=="record"): return

            try:
                rollGuess=int(tokens[4])
            except Exception:
                rollGuess=0  

            if (tokens[3] == ".dice" or tokens[3] == ".roll"):
                if (len(tokens) > 4):
                    try:
                        snick=self.setSNick(tokens)
                        rollGuess=int(tokens[4])
                        ts=time()
                        d0nkwin=0

                        try:
                            timeleft=(self.scores_tmp[snick]["timestamp"]+6)-ts
                        except Exception:
                            self.scores_tmp[snick]={"timestamp":ts,"lastguess":rollGuess,"lastcount":0}
                            timeleft=(self.scores_tmp[snick]["timestamp"]+6)-ts

                        if (timeleft>1 and timeleft<6 and pm==0):
                            if (self.lastrollnick == tokens[0]):
                                msg=("You can't roll for another %s seconds before another person rolls" % int(timeleft))
                                self.s.send(BYTE(":%s NOTICE %s :%s" % (self.nickName,tokens[0],msg)))
                                return

                        self.scores_tmp[snick]["timestamp"]=ts
                        self.lastrollnick=""

                        if (len(tokens)==6):
                            if(tokens[5]=="spliff"):
                                if(rollGuess!=1):
                                     msg="You can only roll 1 spliff at a time"
                                else:
                                    try: self.scores[snick]["spliffs"]+=1
                                    except: self.scores[snick]["spliffs"]=1
                                    self.load_save_data("scores.data.npy",self.scores)
                                    self.lastrollnick=tokens[0]
                                    msg=("You \002Win\002 %s! (Spliff Roll: <//////////////>~~~ = 420)" % tokens[0])
                                self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,replyTo,msg)))
                                return

                        #if (self.scores_tmp[tokens[0]]["lastguess"] == rollGuess):
                        #    self.scores_tmp[tokens[0]]["lastcount"]+=1
                        #    if (self.scores_tmp[tokens[0]]["lastcount"]>=3):
                        #        msg="You can't guess the same number more than 3 times"
                        #        self.s.send(BYTE(":%s NOTICE %s :%s" % (self.nickName,tokens[0],msg)))
                        #        return
                        #else:
                        #    self.scores_tmp[tokens[0]]["lastcount"]=0
                        #    self.scores_tmp[tokens[0]]["lastguess"]=rollGuess

                        if (rollGuess > 4 and rollGuess < 31):
                            diceRoll1=randint(1,6)
                            diceRoll2=randint(1,6)
                            diceRoll3=randint(1,6)
                            diceRoll4=randint(1,6)
                            diceRoll5=randint(1,6)
                            diceRollTotal=diceRoll1+diceRoll2+diceRoll3+diceRoll4+diceRoll5

                            if (rollGuess == diceRollTotal):
                                msgNick=("You \002Win\002 %s!" % tokens[0])
                                self.scores[snick]["win"]+=1
                                d0nkwin=1
                                try: self.scores[snick]["points"]+=int(self.dscores[rollGuess]*self.dsmp)
                                except: self.scores[snick]["points"]=int(self.dscores[rollGuess]*self.dsmp)
                            else:
                                msgNick=("You Lose %s!" % tokens[0])
                                self.scores[snick]["loss"]+=1
                                try: self.scores[snick]["points"]-=1
                                except: self.scores[snick]["points"]=0

                            msg=("%s (Dice Roll %s/%s/%s/%s/%s = %s)" % (msgNick,self.udice[diceRoll1],self.udice[diceRoll2],self.udice[diceRoll3],self.udice[diceRoll4],self.udice[diceRoll5],diceRollTotal))
                            self.load_save_data("scores.data.npy",self.scores)
                            self.lastrollnick=tokens[0]
                        else:
                            raise Exception()
                    except Exception:
                        msg="You need to provide a number from 5 to 30"
                        self.s.send(BYTE(":%s NOTICE %s :%s" % (self.nickName,tokens[0],msg)))
                        return

                if (len(tokens)==4): msg="Usage: .dice|.roll <#|record|score> [nick]"
                self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,replyTo,msg)))

                if (d0nkwin==1):
                    self.s.send(BYTE(":%s PRIVMSG nab2k :!d0nkwin %s %s %s" % (self.nickName,replyTo,snick,rollGuess)))
      except:
        derp=0

    def dice_record(self,tokens):
        try:
            if (tokens[1] == "PRIVMSG"):
                if not (self.pubCheck(tokens)): return
                if (tokens[3] == ".dice" and tokens[4] == "record" and len(tokens) == 5):
                    scnt=0
                    smax=3
                    sS=sorted(self.scores.keys(), key=lambda y: (self.scores[y]['win']), reverse=True)
                    for k1 in sS:
                        scnt+=1
                        try: vtest=self.scores[k1]["points"]
                        except: self.scores[k1]["points"]=0
                        msg=("\002Player:\002 %s \002Win:\002%s \002Loss:\002%s \002Points:\002%s" % (k1, self.scores[k1]["win"], self.scores[k1]["loss"], self.scores[k1]["points"]))
                        self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))
                        if (scnt >= smax):
                            break
        except Exception:
            return False

    def dice_scores(self,tokens):
      try:
        if (tokens[1] == "PRIVMSG" and len(tokens) > 4):
            if not (self.pubCheck(tokens)): return
            snick=self.setSNick(tokens)
            if (len(tokens)==6):
                player=tokens[5]
            else:
                player=snick
            if (tokens[3] == ".dice" and tokens[4] == "score"):
                try:
                    try: vtest=self.scores[player]["spliffs"]
                    except: self.scores[player]["spliffs"]=0
                    try: vtest=self.scores[player]["points"]
                    except: self.scores[player]["points"]=0
                    msg=("\002Player:\002 %s \002Win:\002%s \002Loss:\002%s \002Points:\002%s \002Spliffs:\002%s" % (player,self.scores[player]["win"],self.scores[player]["loss"],self.scores[player]["points"],self.scores[player]["spliffs"]))
                except Exception:
                    msg=("Player %s doesn't have a score" % player)
                
                self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))
      except:
        derp=0

    def quoteman(self,tokens,line):
      try:
        if (tokens[1] == "PRIVMSG"):
            if not (self.pubCheck(tokens)): return 
            if (tokens[3] == ".quote"):
                msg=("Usage: .quote <#|del|add> [quote text] (Quotes Avail:%s)" % len(self.quotes))
                if (len(tokens) == 5):
                    # Get A Quote
                    try:
                        idx=int(tokens[4])
                        msg=("Quote #%s: %s [\002Added by %s on %s\002]" % (idx,self.quotes[idx]['quote'],self.quotes[idx]['owner'],self.quotes[idx]['date']))
                    except Exception as e:
                        try:
                            if (int(tokens[4])):
                                msg=("Quote #%s doesn't exist" % tokens[4])
                        except Exception as e:
                            msg="You need to provide a number"
                if (len(tokens) > 5):
                    # Add new quote
                    if (tokens[4] == "add"):
                        qn=list(self.quotes.keys())[-1]+1
                        quote=getMessage(line).replace(":.quote add ","")
                        owner=tokens[0]
                        qdate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.quotes[qn]={"quote":quote,"owner":owner,"date":qdate}
                        msg=("Added new quote #%s" % qn)
                    # Delete a quote
                    if (tokens[4] == "del"):
                        try:
                            del self.quotes[int(tokens[5])]
                            msg=("Quote #%s has been deleted" % tokens[5])
                        except Exception as e:
                            msg=("Quote #%s doesn't exist" % tokens[5])

                    self.load_save_data("quotes.data.npy",self.quotes)

                self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))
      except:
        derp=0


    def shouts(self,tokens,line):
        try:
            if (tokens[1] == "PRIVMSG"):
                if not (self.pubCheck(tokens)): return 
                if (tokens[3] == ".shout"):
                    msg=("Type: .shout <nickname> <message>")
                    if (len(tokens) == 4):
                        tokens.append(randint(1,len(self.shout)))
                        
                    if (len(tokens) == 5):
                        # Get A Quote
                        try:
                            sdx=int(tokens[4])
                            msg=("#%s: \002%s:\002 %s" % (sdx,self.shout[sdx]['shoutnick'],self.shout[sdx]['shoutz']))

                        except Exception as e:
                            try:
                                if (int(tokens[4])):
                                    msg=("no exist")
                            except Exception as e:
                                msg="Type: .shout <nickname> <message>"        

                    if (len(tokens) > 5):
                        try:
                            # Add new quote
                            sn=(len(self.shout)+1)
                            shoutnick=tokens[4]
                            shoutz=getMessage(line).replace((":.shout %s " % shoutnick),"") 
                            self.shout[sn]={"shoutnick":shoutnick,"shoutz":shoutz}
                            msg=("Added shout to %s" % sn)
                            self.load_save_data("shout.data.npy",self.shout)
                        except Exception as e:
                            msg="Something bad happened"        

                self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))
        except:
            derp=0
        
    def chanman(self,tokens):
      try:
        if (tokens[1] == "PRIVMSG"):
            if (tokens[3] == ".chan"):
                if (len(fnmatch.filter(self.master,self.setSNick(tokens)))==0): return # MASTER ACCESS CHECK
                msg="Usage: .chan <join|part|list> [#chan]"
                if (len(tokens) == 5):
                    if (tokens[4] == "list"):
                        msg="I am on the following channels:"   
                        for channel, v in self.channels.items():
                            msg=("%s %s" % (msg,channel))
                        msg.strip()
                if (len(tokens) > 5):
                    if (tokens[4] == "join"):
                        self.channels[tokens[5]]=tokens[0]
                        self.s.send(BYTE("JOIN %s" % tokens[5]))
                        msg=("Joined channel %s" % tokens[5])
                    if (tokens[4] == "part"):
                        del self.channels[tokens[5]]
                        self.s.send(BYTE("PART %s" % tokens[5]))
                        msg=("Parted channel %s" % tokens[5])

                    self.load_save_data("channels.data.npy",self.channels)

                self.s.send(BYTE(":%s NOTICE %s :%s" % (self.nickName,tokens[0],msg)))
      except:
        derp=0

    def userman(self,tokens,line):
      try:
        if (tokens[1] == "PRIVMSG"):
            if (tokens[3] == ".user"):
                if (len(fnmatch.filter(self.master,self.setSNick(tokens)))==0): return # MASTER ACCESS CHECK
                msg="Usage: .user <addhost|delete|modify|list> [nick] [ident@hostname]"
                if (len(tokens) > 4):
                    if (tokens[4] == "list"):
                        try:
                            if (len(tokens) > 5):
                                msg=("\002User:\002 %s \002Data:\002 %s" % (tokens[5],self.scores[tokens[5]]))
                            else:
                                msg="I have the following users:"
                                for usernick, userdata in self.scores.items():
                                    msg=("%s %s" % (msg,usernick))
                                msg.strip()
                        except:
                            msg="User not found"
                    elif (len(tokens) > 5):
                        if (tokens[4] == "delete"):
                            try:
                                del self.scores[tokens[5]]
                                msg=("Deleted user %s" % tokens[5])
                            except:
                                msg="User not found"
                        if (tokens[4] == "addhost"):
                            try:
                                self.scores[tokens[5]]["hostnames"].append(tokens[6])
                            except:
                                self.scores[tokens[5]]["hostnames"] = [k for k in self.scores[tokens[5]]["hostnames"]]
                                self.scores[tokens[5]]["hostnames"].append(tokens[6])
                            msg=("Added host %s to user %s" % (tokens[6],tokens[5]))
                        if (tokens[4] == "modify"):
                            newdata=getMessage(line).replace((":.user modify %s" % tokens[5]),"")
                            self.scores[tokens[5]]=ast.literal_eval(newdata.strip())
                            msg=("Modified user %s" % tokens[5])

                    self.load_save_data("scores.data.npy",self.scores)

                self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))
      except:
        derp=0

    def fish_slap(self,tokens):
      try:
        if (tokens[1] == "PRIVMSG"):
            if (tokens[3] == ".slap" and len(tokens) > 4):
                random_fish=choice(list(open('fish.txt'))).strip()
                msg=("\x01ACTION slaps %s around a bit with a large %s\x01" % (tokens[4],random_fish))
                self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))
      except:
        derp=0

    def rip(self,tokens):
      try:
        if (tokens[1] == "QUIT" or tokens[1] == "PART"):
            if (len(tokens) == 3):
                self.ripnick = tokens[0]
                return
        if (tokens[1] == "PRIVMSG"):
            if (tokens[3] == ".rip"):
                if (len(tokens) == 5):
                    self.ripnick = tokens[4]
                if (self.ripnick != ""):
                    msg=("R.I.P - %s :(" % self.ripnick)
                    self.ripnick = ""
                else:
                    msg="Usage: .rip [nick]"

                self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))            
      except:
        derp=0

    def pubCheck(self,tokens):
      try:
        if (len(tokens) > 2):
            if (self.nickName == tokens[2]): return False # Only allow public messages
            else: return True
        return False
      except:
        derp=0

    def loadDataFiles(self,tokens):
        try:
            if(tokens!=False):
                if (tokens[1]=="PRIVMSG" and len(tokens)>2):
                    if(tokens[3]==".reload"):
                        if (len(fnmatch.filter(self.master,self.setSNick(tokens)))==0):
                            msg="Reload: Access Denied"
                        else:
                            msg="Reload: OK"
                        self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))            
                    else: return
                else: return
            self.scores=self.load_save_data("scores.data.npy",False)
            self.quotes=self.load_save_data("quotes.data.npy",False)
            self.channels=self.load_save_data("channels.data.npy",False)
            self.shout=self.load_save_data("shout.data.npy",False)
        except:
            derp=0

    def setSNick(self,tokens):
        snick=""
        for k,v in self.scores.items():
            for vv in v["hostnames"]:
                if (len(fnmatch.filter(self.nickhost,vv))>0):
                    snick=k
                    break
        if(snick==""): 
            snick=tokens[0]
            self.scores[snick]={"win":0,"loss":0,"hostnames":self.nickhost}
        return snick

    def chuck(self,tokens,line):       
      try:
        # SEND NAMES COMMAND
        if (tokens[1] == "PRIVMSG"):
            if (tokens[3] == ".chuck"):
                if (len(tokens) == 4):  
                    readBuffer=""
                    self.s.send(BYTE("NAMES %s" % tokens[2]))
                    self.lastmsg="chuck"
                if (len(tokens) > 4):
                    msg=("\x01ACTION chucks bear at %s! Catch. Drink.\x01" % tokens[4])
                    self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[2],msg)))
        # GET NAMES ON NEXT MESSAGE
        elif (tokens[1] == "353"):
           if(self.lastmsg=="chuck"):
               rnick=self.nickName
               while(rnick==self.nickName):
                   rnick=re.sub("[@\+\!~]","",choice(getMessage(line).replace("@ #donk :","").split(" ")))
               msg=("\x01ACTION chucks bear at %s! Catch. Drink.\x01" % rnick)
               self.s.send(BYTE(":%s PRIVMSG %s :%s" % (self.nickName,tokens[4],msg)))
               self.lastmsg=""
      except:
        derp=0          

    # Save or Load dict data
    #

    def load_save_data(self,sfile,data):
        # Save dict data  to file
        if (data != False):
            np.save(sfile, data)
            print("*** Saved Data to: %s" % sfile)
            return True

        # Load from file to dict data
        if (data == False):
            # Return an empty dict if file doesnt exist
            if not (os.path.isfile(sfile)):
                return {}
            data=np.load(sfile).item()
            print("*** Loaded Data from: %s" % sfile)
            return data

        return False

    #
    # TOKEN HANDLER STUFF
    #

    def makeTokens(self, line):
        line = line.rstrip()
        tokens = line.split(" ")
        uhdata = getUser(tokens)
        tokens[0] = uhdata[0]
        try: self.nickhost=[uhdata[1]]
        except: self.nickhost=[]
        index = self.getStartingIndex(line)
        if (len(tokens) > index):
                tokens[index] = tokens[index][1:]
        tokens = list(filter(lambda x: x != "", tokens))
        return tokens

    def getStartingIndex(self, tokens):
        startingIndex = 1
        tokens = tokens.split(" ")
        while (startingIndex < len(tokens)-1 and tokens[startingIndex][0] != ":"):
            startingIndex += 1
        return startingIndex


main()
