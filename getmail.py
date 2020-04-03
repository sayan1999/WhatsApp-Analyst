from mail.mailman import MailReader

reader=MailReader('./mail/mail.json')
while True:
    reader.readmail()