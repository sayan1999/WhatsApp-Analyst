from lib.mail.mailman import MailReader
from lib.logger.log import log

reader=MailReader()
while True:
    reader.readmail()