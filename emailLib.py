from . import emailReader
from . import emailWriter

class emailHandler:
  class emailIterator:
    def __init__(self, mailReader):
      self.mailReader = mailReader
    
    def __iter__(self):
      return self
    
    def __next__(self) -> emailReader.email:
      try:
        nextEmail = self.mailReader.getNext()
        if nextEmail is None:
          raise StopIteration
        return nextEmail
      except IndexError:
        raise StopIteration 
    
    def __length__(self) -> int:
      return len(self.mailReader.IDs)
  
  def __init__(self, username: str, password: str, imap_url: str, smpt_url: str):
    self.mailReader = emailReader.mailReader(username, password, imap_url)
    self.mailWriter = emailWriter.mailWriter(username, password, smpt_url)
  
  def getAllEmails(self,reloadInbox: bool = True) -> emailIterator:
    if reloadInbox:
      self.mailReader.updateInbox()
    return self.emailIterator(self.mailReader)
  
  def sendEmails(self, subject: str, body: str, recipients: str | list[str]):
    self.mailWriter.createEmail(subject, body)
    self.mailWriter.sendEmail(recipients)
  
  def specific(self, box: str | None = None, sender: str | None = None, unread: bool = False) -> None:
    if box is None:
      box = "inbox"
    if sender is None:
      sender = ""
    elif not sender.startswith('FROM "'):
      sender = 'FROM "{}"'.format(sender)
    self.mailReader.updateInbox(targetBox=box, unread=unread, term=sender)
  
  def specificList(self, box: str | None = None, sender: str | None = None, unread: bool = False) -> list[emailReader.email]:
    if box is None:
      box = "inbox"
    if sender is None:
      sender = ""
    else:
      sender = 'FROM "{}"'.format(sender)
    self.specific(box, sender, unread)
    matches: list[emailReader.email] = []
    for email in self.getAllEmails(reloadInbox=False):
      if sender.lower() in email.sender.lower():
        matches.append(email)
    return matches