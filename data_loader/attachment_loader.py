from collections import Counter, OrderedDict
from nltk.corpus import stopwords
from string import punctuation
import pandas as pd
import emoji
from os import scandir, listdir
from os.path import isdir
from utils.fileReadUtils import elementsOf

class Chat_loader:

    def __init__(self):

        self.__clientName = ''
        self.__friends = []
        self.__dir = './attachments/' + '03:04:2020_10:29:20.918717_Sayan Dey <mr.sayan.dey@gmail.com>'
        self.__data = {}
        self.__getFiles()
        self.__readDir()        
    
    # TODO
    def __seekForInbox(self):
        pass

    def __validate_names(self, names):

        copiednames=[name for name in names]
        for name in copiednames:
            if name not in self.__friends:
                self.__clientName=name
                if name in copiednames:
                    copiednames.remove(name)
                break

        if len(copiednames)>1 :
            # It's a group
            return None

        return copiednames[0]


    def __getFiles(self):
        self.__files = [self.__dir + '/' + filename for filename in listdir(self.__dir) if filename.endswith('.txt')]
        self.__friends = [filename.split('_with_')[1][:-4] for filename in listdir(self.__dir) if filename.endswith('.txt') == True]
    
    def __readDir(self):

        for file in self.__files:
            data = elementsOf(file)
            names=set([d['Author'] for d in data])
            friend = self.__validate_names(names)
            if friend != None:
                self.__data[friend] = data

    def getData(self):
        return {"User" : self.__clientName, "Friends" : self.__friends, "Data" :self.__data}

if __name__ == '__main__':

    print(Chat_loader().getData())