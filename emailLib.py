from . import emailReader
from . import emailWriter
from typing import Callable

class email:
  def __init__(self, subject, sender, date, body, idNumber, markedAsReadFunc: Callable[["email | None", bytes | None], None] | None = None):
    self.subject: str = subject
    self.sender: str = sender
    self.date: str = date
    self.body: str = body
    self.idNumber: bytes = idNumber
    self.markFunc: Callable[["email | None", bytes | None], None] | None = markedAsReadFunc 
  def markAsRead(self):
    if self.markFunc is not None:
      self.markFunc(self,None)

class emailHandler:
  class emailIterator:
    def __init__(self, mailReader):
      self.mailReader = mailReader
    
    def __iter__(self):
      return self
    
    def __next__(self) -> email:
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
  
  def lock(self):
    self.mailReader.lock()
    self.mailWriter.lock()
  
  def unlock(self, username: str, password: str, imap_url: str, smpt_url: str):
    self.mailReader.unlock(username, password, imap_url)
    self.mailWriter.unlock(username, password, smpt_url)
  
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
    matches: list[email] = []
    for email_ in self.getAllEmails(reloadInbox=False):
      if sender.lower() in email_.sender.lower():
        matches.append(email_)
    return matches