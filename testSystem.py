userName,password,service_in,service_out = (line.strip() for line in open(".secret").readlines())
import emailReader as er 
import emailWriter as ew

#emails = er.mailReader(userName, password, service_in)
#while True:
#  try:
#    email = emails.getNext()
#    print("Subject: {}".format(email.subject))
#    print("From: {}".format(email.sender))
#    print("Date: {}".format(email.date))
#    print("Body: {}".format(email.body))
#    print("ID: {}".format(email.idNumber))
#    print("\n\n")
# except Exception as e:
#    print(e)
#    break

emailWriter = ew.mailWriter(userName, password, service_out)

subject = "Test Email"
body = "This is a test email sent from the email sender script"
emailWriter.createEmail(subject, body)
emailWriter.sendEmail("test@dendersen.dk")
