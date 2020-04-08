from lib.mail.mailman import MailReader
from lib.maillogger.log import log

reader=MailReader(config='lib/mail/mail.json', logger=log)
reader.readmail()