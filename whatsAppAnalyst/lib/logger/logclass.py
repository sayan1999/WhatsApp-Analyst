import logging
import sys
import colorlog
from colorlog import ColoredFormatter
import traceback
from functools import partial
import warnings
from pytz import timezone, utc
import datetime
from os.path import isdir
from os import makedirs

toSuppressWarns=[
    'font.load_char(ord(s), flags=flags)',
    'missing from current font',
    'Tokenizing the stop words generated tokens',
    'sorted(inconsistent))',
    'font.set_text(s, 0.0, flags=flags)',
    'Attempting to set identical bottom == top == 0',
    'extent=[x,x+w,y,y+h], aspect="auto"'
]

def customTime(*args):
    utc_dt = utc.localize(datetime.datetime.utcnow())
    my_tz = timezone("Asia/Calcutta")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()

class WarnStreamToLogger(object):

    def __init__(self, logger, log_level=logging.WARN):
        self.logger, self.log_level = logger, log_level
         
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            for warnline in toSuppressWarns:
                if warnline in line:
                    return
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

def errHandler(logger, type, value, tb):
    trace=traceback.format_tb(tb)
    logger.error("\n".join([str(value)]+trace))

class StreamToLogger(object):

    def __init__(self, logger, log_level):
        self.logger, self.log_level = logger, log_level
         
    def write(self, buf):
        # for line in buf.rstrip().splitlines():
        #         self.logger.log(self.log_level, line.rstrip())
        self.logger.log(self.log_level, buf)

    def flush(self):
        pass

class Logger():

    _instance=None
    log=None

    def __new__(self):

        if not self._instance:
            self._instance=super(Logger, self).__new__(self)
        Logger.__setLogger()
        return self._instance

    def getLogger(self):
        return self.log

    @staticmethod
    def __setLogger():

        print("\n\n\n------------------------------------------------------New Session--------------------------------------------------\n\n\n")
        mainlogger = logging.getLogger()
        
        logFormatterforConsole = ColoredFormatter(
        '%(log_color)s%(levelname)-8s %(black)s%(bg_cyan)s%(asctime)s%(reset)s %(purple)s%(threadName)-14s %(black)s%(bg_cyan)s%(funcName)s in %(module)s:%(lineno)d%(reset)s\n %(log_color)s%(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
        logFormatterforConsole.converter = customTime
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(logFormatterforConsole)
        mainlogger.addHandler(consoleHandler)

        if not isdir("../logs"):
            makedirs("../logs")
        logFormatterforFile=logging.Formatter('%(levelname)-8s %(asctime)s %(threadName)-14s %(funcName)s in %(module)s:%(lineno)d\n %(message)s')    
        logFormatterforFile.converter = customTime
        fileHandler = logging.FileHandler("{0}/{1}.logging".format("../logs", "log"))
        fileHandler.setFormatter(logFormatterforFile)
        mainlogger.addHandler(fileHandler)
        
        sys.stdout = StreamToLogger(mainlogger, logging.INFO)
        sys.stderr = WarnStreamToLogger(mainlogger, logging.WARN)        

        err=partial(errHandler, mainlogger)   
        sys.excepthook = err

        mainlogger.setLevel(logging.INFO)
        Logger.log=mainlogger

        

if __name__ == '__main__':
    raise ValueError