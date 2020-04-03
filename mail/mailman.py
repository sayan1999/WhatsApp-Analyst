import imaplib
import string, random
from io import StringIO
import email, mailparser
from datetime import datetime
from json import loads as loadjson
from json import dump as dumpjson
from os import mkdir as makedir
from os.path import isdir
from email.header import decode_header

def checkORmake_dir_file(cd, dirname, filename):
    if not isdir('./' + cd + '/' + dirname):
        makedir('./' + cd + '/' + dirname)
    
    return './' + cd + '/' + dirname + '/' + filename

def curtime():
    return datetime.now().strftime("%d:%m:%Y_%H:%M:%S.%f")

class Mailer:

    def __init__(self):

        self.__USER  = "annabelleconjuring11@gmail.com"
        self.__PASSWORD = "con1ann1"
        self.__SMTP_SERVER = "imap.gmail.com"
        self.__SMTP_PORT = 993
        self.__mail = None
        self.__login()

    def __login(self):

        self.__mail = imaplib.IMAP4_SSL(self.__SMTP_SERVER)
        self.__mail.login(self.__USER, self.__PASSWORD)
        self.__mail.select('inbox')

    def __log(self, id, msg):
        print(id.decode('utf-8') + '-> From : ' + msg["From"] + ' Subject : ' + msg["Subject"])

    def __storeIntoFile(self, filename, sender, content):

        directoryName=self.__timestampForThisMsg+'_'+sender
        filename=curtime()+'_with_'+filename+'.txt'

        filepath=checkORmake_dir_file('attachments', directoryName.replace('/', ':'), filename.replace('/', ':'))

        with open(filepath, 'wb+') as outfile:
            outfile.write(content)        

    def __leave_trace(self, sender):

        if isdir('./attachments/' + self.__timestampForThisMsg+'_'+sender):
            endAckFilepath='./attachments/' + self.__timestampForThisMsg+'_'+sender+'/ends'
            open(endAckFilepath, 'w+')


    def __extractTXT(self, msg): 
        
        if msg.is_multipart():
            self.__timestampForThisMsg=curtime()
            for part in msg.walk():
                ctype, filename = part.get_content_type(), part.get_filename()
                if (ctype == 'text/plain') and not(filename == None):
                    filename, encoding=decode_header(filename)[0]
                    if encoding:
                        filename=filename.decode(encoding)
                    print(filename)
                    if (filename.endswith('.txt') and filename.startswith('WhatsApp Chat with ')):
                        filename=filename[19:-4]
                        self.__storeIntoFile(filename, msg["From"], part.get_payload(decode=True))
        
        self.__leave_trace(msg["From"])

        
    def readmail(self):        

        _, data = self.__mail.search(None, '(UNSEEN)')
        mail_ids = data[0].split()

        if len(mail_ids) == 0:
            return False

        for id in mail_ids:

            _, data = self.__mail.fetch(id, '(BODY.PEEK[])')
            curmsg = email.message_from_string(data[0][1].decode('utf-8'))

            self.__log(id, curmsg)
            self.__extractTXT(curmsg)
            # self.__mail.store(id,'+FLAGS', '(\\SEEN)')
        return True


if __name__ == '__main__':
    
    Mailer().readmail()