from mail.mailman import MailReader

reader=MailReader()
while True:
    reader.readmail()