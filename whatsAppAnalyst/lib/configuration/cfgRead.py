import json
jsonobj=json.load(open('lib/configuration/conf.json'))
IMAP4_SERVER = jsonobj["IMAP4_SERVER"]
IMAP4_PORT = jsonobj["IMAP4_PORT"]  
SMTP_SERVER = jsonobj["SMTP_SERVER"]
SMTP_PORT = jsonobj["SMTP_PORT"]   
MAILPOLLINGTIMEOUT = jsonobj["MAILPOLLINGTIMEOUT"]    
DIRECTORYCHECKINGTIMEOUT=jsonobj["DIRECTORYCHECKINGTIMEOUT"]
KEYFILE=jsonobj["KEYFILE"]