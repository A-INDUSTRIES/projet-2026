from base64 import urlsafe_b64decode, urlsafe_b64encode
import json

class Message():
    def __init__(self, id, historyId, date, sender, subject, content):
        self._id = id
        self.historyId = historyId
        self.date = date
        self.sender = sender
        self.subject = subject
        self.content = content

    def id(self):
        return self._id

    @staticmethod
    def from_raw(msg):
        id = msg["id"]
        historyId = msg["historyId"]
        date = int(msg["internalDate"])
        content = ""
        payload = msg['payload']
        if "text/html" in payload['mimeType']:
            content = urlsafe_b64decode(payload['body']['data']).decode()
        elif "multipart" in payload['mimeType']:
            for part in payload['parts']:
                if "text/html" in part['mimeType']:
                    content += urlsafe_b64decode(part['body']['data']).decode()
        for header in payload['headers']:
            if header['name'] == "Subject":
                subject = header["value"]
            if header['name'] == 'From':
                sender = header["value"]
        return Message(id, historyId, date, sender, subject, content)
    
class MessageDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def decode(self, s, **kwargs):
        data = super().decode(s, **kwargs)
        return [Message(v["id"], v["historyId"], v["date"], v["sender"], v["subject"], v["content"]) for v in data if isinstance(v, dict)]
    
class MessageEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def default(self, o):
        if isinstance(o, Message):
            return {"id": o.id(), "historyId": o.historyId, "date": o.date, "sender": o.sender, "subject": o.subject, "content": o.content}
        return super().default(o)