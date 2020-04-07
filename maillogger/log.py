import logging
import sys

log=None

def init():

    global log

    if log:
        return

    logFormatter=logging.Formatter('[%(asctime)s {%(threadName)-12.12s} %(module)s:%(lineno)d]: %(message)s')
    mainlogger = logging.getLogger("Instantinopaul")
    
    mainlogger.setLevel(logging.INFO)
    
    fileHandler = logging.FileHandler("{0}/{1}.logging".format("logs", "mails"))
    fileHandler.setFormatter(logFormatter)
    mainlogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    mainlogger.addHandler(consoleHandler)

    log=mainlogger

init()