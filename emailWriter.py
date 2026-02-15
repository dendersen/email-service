import smtplib
from email.message import EmailMessage

class mailWriter:
  def __init__(self, username: str, password: str, smpt_url: str):
    self.username: str = username
    self.password: str = password
    self.smpt_url: str = smpt_url
    self.currentEmail: EmailMessage | None = None
    self.recipients: list[str] | str = []
  
  def createEmail(self, subject: str, body: str):
    self.currentEmail = EmailMessage()
    self.currentEmail.set_content(body)
    self.currentEmail['Subject'] = subject
    self.currentEmail['From'] = self.username
  
  def sendEmail(self, recipients: str | list[str]):
    if self.currentEmail is None:
      raise ValueError("No email created, call createEmail() before sending an email")
    
    if recipients is None:
      if self.recipients is None:
        raise ValueError("No recipients specified, call sendEmail() with a recipient or set recipients attribute before sending an email")
      elif type(recipients) == list:
        recipients = self.recipients
      elif type(recipients) == str:
        recipients = [self.recipients]
      else:
        raise ValueError("no valid recipients specified, recipients must be a string or a list of strings")
    elif type(recipients) == str:
      recipients = [recipients]
    elif type(recipients) != list:
      raise ValueError("Recipients must be a string or a list of strings")
    
    with smtplib.SMTP_SSL(self.smpt_url) as server:
      server.login(self.username, self.password)
      
      for recipient in recipients if type(recipients) == list else [recipients]:
        errors = server.send_message(self.currentEmail, to_addrs=recipient)
        if errors is not None and len(errors) > 0:
          raise ValueError("Failed to send email to recipient {}, error: {}".format(recipient, errors))