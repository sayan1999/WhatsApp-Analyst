import datetime
from os import makedirs
from ..mainlogger.log import log
from ..message_class.msg_class import Msg
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
        except ValueError as e:
            log.info(e)
            log.info("Could not readline " + raw)
            return "changed"
        else:
            return {'DateTime': dateNtime, 'Author' : author, 'Message' : message, 'Emoji' : emojis}
    return None    

def elementsOf(textfile, msg, dtimefmt='%m/%d/%y %I:%M %p', trial=0):
    opt_dtimefmt=['%d/%m/%y %I:%M %p', '%m/%d/%y %H:%M', '%d/%m/%Y %I:%M %p', '%m/%d/%Y %I:%M %p', '%m/%d/%Y %H:%M']
    data=[]
    for line in readfile(textfile):
        formatted = format(line, dtimefmt)
        if formatted == 'changed':
            trial+=1
            if trial < 5:
                log.info("Trying deprecated dtimeformat: " + opt_dtimefmt[trial-1])
                return elementsOf(textfile, msg, opt_dtimefmt[trial-1], trial)
            else:
                msg.new_msg("Could not understand data format")
                log.info("Couldn't understand data format")
                return []
        if formatted != None:
            if formatted['Message'] != '':
                data.append(formatted)
    log.info("Successfully read "+ textfile)
    return data 

def makedirectory(path):
    makedirs(path)
    return path