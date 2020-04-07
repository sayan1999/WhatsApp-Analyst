import imaplib, string, random
from time import sleep
from io import StringIO
import email, mailparser
from datetime import datetime
from json import loads as loadjson
from json import dump as dumpjson
from os import makedirs
from os.path import isdir
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from os import listdir
import smtplib
import json
from maillogger.log import log
from os.path import join as pathjoin

def extractAddr(fullAddr):
    if '<' in fullAddr:
        fullAddr=fullAddr.split('<')[1]
    if '>' in fullAddr:
        fullAddr=fullAddr.split('<')[0]

    return fullAddr

def curtime():
    return datetime.now().strftime("%Y:%m:%d_%H:%M:%S.%f")

class Mailer:

    def __init__(self, config):
        
        jsonobj = json.load(open(config))
        self.USER  = jsonobj['USER']
        self.PASSWORD = jsonobj['PASSWORD']
        self.IMAP4_SERVER = jsonobj["IMAP4_SERVER"]
        self.IMAP4_PORT = jsonobj["IMAP4_PORT"]  
        self.SMTP_SERVER = jsonobj["SMTP_SERVER"]
        self.SMTP_PORT = jsonobj["SMTP_PORT"]   
        self.TIMEOUT = jsonobj["TIMEOUT"]     

class MailReader(Mailer):

    def __init__(self, config):

        Mailer.__init__(self, config=config)        
        self.__IMAPlogin()

    def __IMAPlogin(self):
        
        self.__mail = imaplib.IMAP4_SSL(self.IMAP4_SERVER, self.IMAP4_PORT)
        self.__mail.login(self.USER, self.PASSWORD)
        log.info("Logged into IMAP4 server successfully")

    def __storeIntoFile(self, filename, content):

        if not isdir(self.__dirpath):
            makedirs(self.__dirpath)
        
        filepath=pathjoin(self.__dirpath, filename)
        with open(filepath, 'wb+') as outfile:
            outfile.write(content)
        log.info("Contents written in " + filepath)        

    def __leave_trace(self, sender):
        
        endAckFilepath=pathjoin(self.__dirpath, 'ends')
        try:
            open(endAckFilepath, 'w+')
        except FileNotFoundError:
            log.info("No suitable attachment found, dummy file not created")
        else:
            log.info("Dummy file for completion acknowledgement created")


    def __extractTXT(self, msg): 
        
        if msg.is_multipart():
            self.__timestampForThisMsg=curtime()
            self.__dirpath=pathjoin('attachments', self.__timestampForThisMsg+'_'+msg['From'].replace('/', ':'))
            for part in msg.walk():
                ctype, filename = part.get_content_type(), part.get_filename()
                if (ctype == 'text/plain') and not(filename == None):
                    log.info("Got a file attachment: "+filename)
                    filename, encoding=decode_header(filename)[0]
                    if encoding:
                        filename=filename.decode(encoding)
                    if (filename.endswith('.txt') and filename.startswith('WhatsApp Chat with ')):
                        log.info("The file attachment as per naming conventions of WhatsApp chat exports")
                        chatFileWith=filename[19:]
                        filename=(curtime()+'_with_'+chatFileWith).replace('/', ':')
                        self.__storeIntoFile(filename, part.get_payload(decode=True))

                    else:
                        log.info("The file was rejected for not matching with naming conventions of WhatsApp chat exports")
        
            self.__leave_trace(msg["From"])

        
    def readmail(self):        

        self.__mail.select('inbox')
        _, data = self.__mail.search(None, '(UNSEEN)')
        mail_ids = data[0].split()

        if len(mail_ids) == 0:
            print('...')
            sleep(self.TIMEOUT)
            self.readmail()
        else:
            log.info("Unread messages in Inbox")

        for id in mail_ids:

            _, data = self.__mail.fetch(id, '(BODY.PEEK[])')
            curmsg = email.message_from_string(data[0][1].decode('utf-8'))

            log.info("Recived message from " + curmsg["From"] + "with sub: " + curmsg["Subject"] + "\nMessage ID: " + id.decode('utf-8'))
            self.__extractTXT(curmsg)
            self.__mail.store(id,'+FLAGS', '(\\SEEN)')
        
        self.readmail()

class MailSender(Mailer):

    def __init__(self, config):

        Mailer.__init__(self, config=config)
        self.__SMTPlogin()

    def __SMTPlogin(self):

        self.__session = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
        self.__session.starttls()
        self.__session.login(self.USER, self.PASSWORD)
        log.info("Logged into SMTP server successfully")
        

    def sendmail(self, recipient, fullAddr, attachment_dir=None, fileExtension='.png', msg=[]):
        
        addr=extractAddr(fullAddr)
        log.info("Mailid extracted: "+addr+" for recipient " + recipient)
        msg=self.constrMail(recipient, addr, attachment_dir, fileExtension, msg)
        text = msg.as_string()
        log.debug("Constructed message: "+text)
        log.info("Sending to " + self.USER + "  at " +addr+".....")
        self.__session.sendmail(self.USER, addr, text)
        log.info("Message has been sent to " + addr " successfully")
        self.__session.quit()

    def init_msg(self, recipient, addr, msg):

        mail_content = "Hello "+recipient+''',
    Greetings from Instantinopaul.
    Your chat was very tasty.... kidding :)
    Find out the attachments.
    Have a nice day :)
    '''+'\n'+"\n".join(msg)
        message = MIMEMultipart()
        message['From'] = self.USER
        message['To'] = addr
        message['Subject'] = 'Results from Instantinopaul Your Personal Data Analyzer'
        message.attach(MIMEText(mail_content, 'plain'))

        return message

    def constrMail(self, recipient, addr, attachment_dir, fileExtension, msg):
        
        message=self.init_msg(recipient, addr, msg) 

        if  attachment_dir:

            if not (isdir(attachment_dir)):
                log.error(attachment_dir + "doesn't exist")
                return message

            attach_files = [(filename, pathjoin(attachment_dir, filename)) for filename in listdir(attachment_dir) if filename.endswith(fileExtension)]
            for attach_file_name, filepath in attach_files:

                data = open(filepath, 'rb').read()
                attachment=MIMEImage(data, name=attach_file_name)
                message.attach(attachment)
                log.info(filepath+" has been attached")
        return message