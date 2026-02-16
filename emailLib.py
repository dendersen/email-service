import emailReader
import emailWriter

class emailHandler:
  class emailIterator:
    def __init__(self, mailReader):
      self.mailReader = mailReader
    def __iter__(self):
      self.mailReader.updateInbox()
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
  def getAllEmails(self) -> emailIterator:
    return self.emailIterator(self.mailReader)
  def sendEmails(self, subject: str, body: str, recipients: str | list[str]):
    self.mailWriter.createEmail(subject, body)
    self.mailWriter.sendEmail(recipients)
