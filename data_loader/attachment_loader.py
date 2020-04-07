from collections import Counter, OrderedDict
from nltk.corpus import stopwords
from string import punctuation
import pandas as pd
import emoji
from mainlogger.log import log
from os import scandir, listdir
from os.path import isdir
from utils.fileReadUtils import elementsOf
from os.path import join as pathjoin
from Message_Class.msg_class import Msg

def extractAddr(fullAddr):
    if '<' in fullAddr:
        fullAddr=fullAddr.split('<')[1]
    if '>' in fullAddr:
        fullAddr=fullAddr.split('<')[0]

    return fullAddr

class Chat_loader:

    def __init__(self, dirname):

        self.__clientName = 'You'
        self.__friends = []
        self.__dir = pathjoin('attachments', dirname)
        log.info("Reading " + self.__dir)
        self.__data = {}
        self.__msg_resp=Msg()
        self.__getFiles()
        self.__readDir()    
    
    # TODO
    def __seekForInbox(self):
        pass

    def __validate_names(self, friend, names_appeared_inChat):

        names_inChat=list(names_appeared_inChat)

        if friend in names_inChat:
            names_inChat.remove(friend)

        if len(names_inChat)>1 :
            
            self.__msg_resp.new_msg("Sorry, You have sent a group chat or your filename doesn't have your friend name.")
            log.info("Rejected group chat or incorrect filename")
            return self.__clientName, 0
         
        
        if len(names_inChat) == 0:            
            return self.__clientName, 1

        return names_inChat[0], 1


    def __getFiles(self):
        
        self.__friendfilemap = {filepath.split('_with_')[1][:-4]:pathjoin(self.__dir, filepath) for filepath in listdir(self.__dir) if filepath.endswith('.txt') == True}

    def __readDir(self):

        self.__msg_resp.new_msg("We handle one-to-one chats only, so we are looking for same name of yours in the files, if you have different names the results won't be as expected.")
        for friend, filepath in self.__friendfilemap.items():

            data = elementsOf(filepath, self.__msg_resp)
            names_appeared_inChat=set([d['Author'] for d in data])
            self.__clientName, status = self.__validate_names(friend, names_appeared_inChat)
            if status:
                self.__data[friend] = data

            for friend, data in self.__data.items():
                friends=list(set([d['Author'] for d in data]))
                if friend in friends:
                    friends.remove(friend)
                if len(friends):
                    if self.__clientName != friends[0]:
                        self.__msg_resp.new_msg("Sorry, You have sent file with incorrect filename.")
                        log.info("Rejected incorrect filename")
                        self.__data.pop(friend)
                       
        for data in self.__data.values():
            self.__friends+=list(set([d['Author'] for d in data]))
            if self.__clientName in self.__friends:
                self.__friends.remove(self.__clientName)

    def getData(self):
        return {"MailID": extractAddr(self.__dir), "User" : self.__clientName, "Friends" : self.__friends, "Data" :self.__data, "Response" : self.__msg_resp.get_msg()}

