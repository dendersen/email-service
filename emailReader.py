import imaplib
from email.parser import Parser
from email.policy import default
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

class mailReader:
  def __init__(self, username: str, password: str, imap_url: str):
    self.username: str = username
    self.password: str = password
    self.imap_url: str = imap_url
    self.IDs: list[bytes] = []
    self.nextIndex: int = -1
    self.updateInbox()
    self.latestEmail: email | None = None
  
  def updateInbox(self, targetBox:str = "inbox", unread: bool = True, term: str = ""):
    with imaplib.IMAP4_SSL(self.imap_url) as mail:
      status, response = mail.login(self.username, self.password)
      if status != "OK":
        raise ValueError("Failed to login")
      
      status, response = mail.select(targetBox, readonly=True)
      if status != "OK":
        raise ValueError("Failed to select inbox")
      if(type(response) != list):
        raise ValueError("Unexpected response type: {}".format(type(response)))
      if(type(response[0]) != bytes):
        raise ValueError("Unexpected response content type: {}".format(type(response[0])))
      
      if(unread):
        status, response = mail.search(None, "(UNSEEN)",term)
      else:
        status, response = mail.search(None, "ALL", term)
      if status != "OK":
        raise ValueError("Failed to search for unseen emails")
      if(type(response) != list):
        raise ValueError("Unexpected search response type: {}".format(type(response)))
      
      emailIds = response[0].split()
      
      self.IDs = emailIds
      self.nextIndex = 0
  
  def getNext(self) -> email:
    if(self.nextIndex >= len(self.IDs)):
      raise IndexError("No more emails to read, run updateInbox() to get all unread emails")
    with imaplib.IMAP4_SSL(self.imap_url) as mail:
      status, response = mail.login(self.username, self.password)
      if status != "OK":
        raise ValueError("Failed to login")
      status, response = mail.select("inbox", readonly=True)
      if status != "OK":
        raise ValueError("Failed to select inbox")
      
      typ, data = mail.fetch(str(self.IDs[self.nextIndex], 'utf-8'),'(RFC822)')
      if typ != "OK":
        raise ValueError("Failed to fetch email with ID {}".format(self.IDs[self.nextIndex]))
      if(data is None or len(data) == 0):
        raise ValueError("No data returned for email with ID {}".format(self.IDs[self.nextIndex]))
      
      if(type(data[0]) != tuple):
        raise ValueError("Unexpected data format for email with ID {}: {}".format(self.IDs[self.nextIndex], type(data[0])))
      msg = Parser(policy=default).parsestr(data[0][1].decode())
      
      subject = msg["subject"]
      sender = msg["from"].split("<")[-1].split(">")[0] #get email from sender field, works for both "Name <email>" and "email"
      date = msg["date"]
      body = msg.get_body(preferencelist=('plain'))
      if body is not None:
        body = body.get_content()
      else:
        body = ""
      emailObj = email(subject, sender, date, body, self.IDs[self.nextIndex], self.markAsRead)
      self.nextIndex += 1
      self.latestEmail = emailObj
      return emailObj
  
  def markAsRead(self, email: email | None = None, idNumber: bytes | None = None):
    with imaplib.IMAP4_SSL(self.imap_url) as mail:
      emailID = None
      if email is not None:
        emailID = email.idNumber
      elif idNumber is not None:
        emailID = idNumber
      else:
        raise ValueError("Either an Email object or an ID number must be provided")
      
      status, response = mail.login(self.username, self.password)
      if status != "OK":
        raise ValueError("Failed to login")
      status, response = mail.select("inbox")
      if status != "OK":
        raise ValueError("Failed to select inbox")
      
      typ, response = mail.store(str(emailID, 'utf-8'), '+FLAGS', '\\Seen')
      if typ != "OK":
        raise ValueError("Failed to mark email with ID {} as read".format(emailID))