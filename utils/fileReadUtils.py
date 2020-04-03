import datetime

def readfile(textfile):
    file = open(textfile, 'r')
    text = file.readlines()
    file.close()
    return text    

def format(line):
    
    if ' - ' not in line or ', ' not in line or ': ' not in line:
        return None
    
    try:
        datetimestr, raw = line.split(' - ', 1)
        date, time = datetimestr.split(', ', 1)
    
    except ValueError:
        print(line)
        return None
    
    if ': ' in raw:
        linemessage = raw.split(': ', 1)        
        if linemessage[1] == '<Media omitted>\n':
            return None
        
        author = linemessage[0]
        message = linemessage[1]
        newdate=datetime.datetime.strptime(date, '%m/%d/%y')
        newtime=datetime.datetime.strptime(time, '%I:%S %p')
        dateNtime=datetime.datetime.strptime(date+' '+time, '%m/%d/%y %I:%S %p')
        return {'Date' : newdate, 'Time' : newtime, 'DateTime': dateNtime, 'Author' : author, 'Message' : message}
    return None    

def elementsOf(textfile):
    data=[]
    for line in readfile(textfile):
        formatted = format(line)
        if formatted != None:
            if formatted['Message'] != '':
                data.append(formatted)
    return data