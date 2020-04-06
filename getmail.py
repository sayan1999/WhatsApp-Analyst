from mail.mailman import MailReader

reader=MailReader(config='./mail/mail.json')
reader.readmail()