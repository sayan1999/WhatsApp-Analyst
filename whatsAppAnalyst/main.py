from lib.logger.log import log
from lib.encryption import encryption
from os import listdir, system
from time import sleep
from os.path import isdir, join as pathjoin, isfile, isdir
from os import makedirs
from _thread import start_new_thread
from threading import Semaphore
import cProfile
import time
import json

import sys, multiprocessing
from lib.mail.mailman import MailReader
from analyzer import Analyst
from lib.configuration.cfgRead import DIRECTORYCHECKINGTIMEOUT, MAXANALYZERTHREADS

semaphore=Semaphore(MAXANALYZERTHREADS)

def mailreader():
    reader=MailReader()
    while True:
        reader.readmail()

def initDir(dirs=['../data/attachments', '../data/images']):
    for directory in dirs:
        if not isdir(directory):
            makedirs(directory)

def analyze(dirpath):

    analyzer=Analyst(dirpath)
    analyzer.start()
    log.info("Ended")

def startAnalyzer(newdir):
     
    global semaphore
    semaphore.acquire()
    start = time.time()  

    print("\n\n\n--------------------------Total analyzers running: {}-----------------------------\n\n\n" .format(MAXANALYZERTHREADS-semaphore._value))

    proc=multiprocessing.Process(target=analyze, args=(newdir,))
    proc.start()
    proc.join()

    end = time.time()
    log.info("Time consumed: {} seconds" .format(end-start))
    print("\n\n\n--------------------------Total analyzers running: {}-----------------------------\n\n\n" .format(MAXANALYZERTHREADS-semaphore._value-1))

    semaphore.release()
    

def checkNewDir():

    newentry=True    
    TIMEOUT=DIRECTORYCHECKINGTIMEOUT

    attachmentdir = '../data/attachments'
    pastdirs = set(listdir(attachmentdir))

    while True:

        if not newentry:
            sleep(TIMEOUT)
            # print('...')

        newentry=False
        newdirs=set(listdir(attachmentdir))

        for newdir in newdirs:
            
            if newdir not in pastdirs:
                newentry=True
                log.info('New entry in ' + attachmentdir + ':   ' + newdir)
                while(not(isfile(pathjoin(attachmentdir, newdir, 'ends')))):
                    log.info("'ends' file not found in " + pathjoin(attachmentdir, newdir))
                    
                start_new_thread(startAnalyzer, (newdir,))
                
        pastdirs=newdirs

if __name__ == '__main__':

    initDir()
    start_new_thread(mailreader, ())
    checkNewDir()

