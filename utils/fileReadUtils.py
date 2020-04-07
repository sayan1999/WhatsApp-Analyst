import datetime
from os import makedirs
from mainlogger.log import log
from Message_Class.msg_class import Msg
import emoji

def readfile(textfile):
    file = open(textfile, 'r')
    text = file.readlines()
    file.close()
    return text    

def format(line, dtimefmt):
    
    if ' - ' not in line or ', ' not in line or ': ' not in line:
        return None
    
    try:
        datetimestr, raw = line.split(' - ', 1)
        date, time = datetimestr.split(', ', 1)
    
    except ValueError as e:
        log.error(e)
        return None
    
    if ': ' in raw:
        linemessage = raw.split(': ', 1)        
        if linemessage[1] == '<Media omitted>\n':
            return None
        
        author = linemessage[0]
        message = linemessage[1]
        emojis=[e for e in message if e in emoji.UNICODE_EMOJI]
        # newdate=datetime.datetime.strptime(date, '%m/%d/%y')
        # newtime=datetime.datetime.strptime(time, '%I:%S %p')
        try:
            dateNtime=datetime.datetime.strptime(date+' '+time, dtimefmt)
        except ValueError:
            return "changed"
        else:
            return {'DateTime': dateNtime, 'Author' : author, 'Message' : message, 'Emoji' : emojis}
    return None    

def elementsOf(textfile, msg, dtimefmt='%m/%d/%y %I:%S %p', trial=False):
    opt_dtimefmt='%d/%m/%y %I:%S %p'
    data=[]
    for line in readfile(textfile):
        formatted = format(line, dtimefmt)
        if formatted == 'changed':
            if not trial:
                log.info("Trying deprecated dtimeformat")
                return elementsOf(textfile, msg, opt_dtimefmt, True)
            else:
                msg.new_msg("Could not understand data format")
                return []
        if formatted != None:
            if formatted['Message'] != '':
                data.append(formatted)
    log.info("Successfully read "+ textfile)
    return data 

def makedirectory(path):
    makedirs(path)
    return path