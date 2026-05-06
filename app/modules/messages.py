from base64 import urlsafe_b64decode, urlsafe_b64encode

class Message():
    def __init__(self, id, sender, subject, content):
        self.id = id
        self.sender = sender
        self.subject = subject
        self.content = content

    def id(self):
        return self.id

    @staticmethod
    def from_raw(msg):
        id = msg["id"]
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
        return Message(id, sender, subject, content)