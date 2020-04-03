import imaplib, string, random
from time import sleep
from io import StringIO
import email, mailparser
from datetime import datetime
from json import loads as loadjson
from json import dump as dumpjson
from os import mkdir as makedir
from os.path import isdir
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from os import listdir
import smtplib
import json

def checkORmake_dir_file(cd, dirname, filename):
    if not isdir('./' + cd + '/' + dirname):
        makedir('./' + cd + '/' + dirname)
    
    return './' + cd + '/' + dirname + '/' + filename

def curtime():
    return datetime.now().strftime("%Y:%m:%d_%H:%M:%S.%f")

class Mailer:

    def __init__(self, filepath):

        jsonobj = json.load(open(filepath))
        self.USER  = jsonobj['USER']
        self.PASSWORD = jsonobj['PASSWORD']

class MailReader(Mailer, filepath):

    def __init__(self):

        Mailer.__init__(self, filepath)
        self.__IMAP4_SERVER = "imap.gmail.com"
        self.__IMAP4_PORT = 993
        self.__IMAPlogin()

    def __IMAPlogin(self):
        self.__mail = imaplib.IMAP4_SSL(self.__IMAP4_SERVER)
        self.__mail.login(self.USER, self.PASSWORD)

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

        self.__mail.select('inbox')
        _, data = self.__mail.search(None, '(UNSEEN)')
        mail_ids = data[0].split()

        if len(mail_ids) == 0:
            sleep(5)
            return False

        for id in mail_ids:

            _, data = self.__mail.fetch(id, '(BODY.PEEK[])')
            curmsg = email.message_from_string(data[0][1].decode('utf-8'))

            self.__log(id, curmsg)
            self.__extractTXT(curmsg)
            self.__mail.store(id,'+FLAGS', '(\\SEEN)')
        return True

class MailSender(Mailer, filepath):

    def __init__(self):

        Mailer.__init__(self, filepath)
        self.__SMTPconn = "smtp.gmail.com"
        self.__SMTP_PORT = 587
        self.__SMTPlogin()

    def __SMTPlogin(self):
        self.__session = smtplib.SMTP('smtp.gmail.com') #use gmail with port
        self.__session.starttls() #enable security
        self.__session.login(self.USER, self.PASSWORD) #login with mail_id and password

    def sendmail(self, recipient, recvAddr, directory):
        
        addr=recvAddr.split('<')[1].split('>')[0]
        message=self.constrMail(recipient, recvAddr, directory)
        text = message.as_string()
        self.__session.sendmail(self.USER, addr, text)
        self.__session.quit()

    def constrMail(self, recipient, recvAddr, directory):
        
        mail_content = "Hello "+recipient+'''
Greetings from Instantinopaul.
Your chat was very tasty.... kidding :)
Find out the attachments.
Have a nice day :)
    '''
        
        message = MIMEMultipart()
        message['From'] = self.USER
        message['To'] = recvAddr
        message['Subject'] = 'Results from Instantinopaul Your Personal Data Analyzer'
        
        message.attach(MIMEText(mail_content, 'plain')) 

        attach_files = [(filename, directory+'/'+filename) for filename in listdir(directory) if filename.endswith('.png')]
        for attach_file_name, filepath in attach_files:

            data = open(filepath, 'rb').read()
            attachment=MIMEImage(data, name=attach_file_name)
            message.attach(attachment)
        
        return message

if __name__ == '__main__':
    m=MailSender()
    m.sendmail('./images/Sayan Dey_2020-04-03 10:56:57.422103', '<mr.sayan.dey@gmail.com>')