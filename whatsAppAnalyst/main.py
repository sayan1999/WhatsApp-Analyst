from lib.encryption import encryption
from os import listdir, system
from time import sleep
from os.path import isdir, join as pathjoin, isfile
from _thread import start_new_thread
import cProfile
import time
import json
from lib.logger.log import log
import sys
from lib.mail.mailman import MailReader
from analyzer import Analyst
from lib.configuration.cfgRead import DIRECTORYCHECKINGTIMEOUT

def mailreader():
    reader=MailReader()
    while True:
        reader.readmail()

def analyze(dirpath):

    analyzer=Analyst(dirpath)
    analyzer.start()
    log.info("Ended")

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
                    
                start = time.time()    
                analyze(newdir)
                end = time.time()
                log.info("Time consumed: {} seconds" .format(end-start))
        pastdirs=newdirs

start_new_thread(mailreader, ())
start_new_thread(checkNewDir, ())


while True:

    sleep(100)


