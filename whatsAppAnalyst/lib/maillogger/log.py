import logging
import sys
import colorlog
from colorlog import ColoredFormatter


log=None

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
                self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

def init():

    global log

    if log:
        return

    print("\n\n\n------------------------------------------------------New Session--------------------------------------------------\n\n\n")
    mainlogger = logging.getLogger()
    
    logFormatterforConsole = ColoredFormatter(
	'%(blue)s%(levelname)-8s %(yellow)s%(asctime)s %(threadName)-14s %(module)s:%(lineno)s\n %(log_color)s%(message)s',
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
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatterforConsole)
    mainlogger.addHandler(consoleHandler)

# "%(levelname)-10s%(reset)s%(asctime)s %(threadName)s %(module)s%(lineno)s       %(message)s"
    logFormatterforFile=logging.Formatter('%(levelname)-8s %(asctime)s %(threadName)-14s %(module)s:%(lineno)s\n %(message)s')    
    fileHandler = logging.FileHandler("{0}/{1}.logging".format("../logs", "mails"))
    fileHandler.setFormatter(logFormatterforFile)
    mainlogger.addHandler(fileHandler)
    
    sys.stdout = StreamToLogger(mainlogger, logging.INFO)
    sys.stderr = StreamToLogger(mainlogger, logging.ERROR)    

    log=mainlogger
    mainlogger.setLevel(logging.INFO)

init()