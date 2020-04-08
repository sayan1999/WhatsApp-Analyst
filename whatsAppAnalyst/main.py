from os import listdir, system
from time import sleep
from os.path import isdir, join as pathjoin, isfile
from _thread import start_new_thread
import cProfile
import time
from lib.mainlogger.log import log
import sys
from lib.mail.mailman import MailReader
from analyzer import Analyst

def mailreader():
    reader=MailReader(config='lib/mail/mail.json', logger=log)
    reader.readmail()

def analyze(dirpath):

    analyzer=Analyst(dirpath)
    analyzer.start()
    log.info("Ended")

def checkNewDir():

    newentry=True
    TIMEOUT=5

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
                print('New entry in ' + attachmentdir + ':   ' + newdir)
                while(not(isfile(pathjoin(attachmentdir, newdir, 'ends')))):
                    print("'ends' file not found in " + pathjoin(attachmentdir, newdir))
                    
                start = time.time()    
                analyze(newdir)
                end = time.time() 
                print("Time consumed: {} seconds" .format(end-start))
        pastdirs=newdirs

start_new_thread(mailreader, ())
start_new_thread(checkNewDir, ())


while True:

    sleep(999999999)


