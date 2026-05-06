from google.auth.transport.requests import Request
from google.auth.credentials import TokenState
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode
from .utils import Singleton, getUserDataPath
from .logger import debug
from .messages import Message

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]

SIGNATURE = "<font style=\"color:rgb(153,153,153)\"><br>Envoyé depuis CommuniquerAvecLesYeux.</font>"

class MailManager(metaclass=Singleton):
    def __init__(self):
        self.creds = None
        self.messages = []
        path = getUserDataPath() / "token.json"
        if path.exists():
            self.creds = Credentials.from_authorized_user_file(path, SCOPES)
            match self.creds.token_state:
                case TokenState.STALE:
                    self.creds.refresh(Request())
                case TokenState.INVALID:
                    self.login()
                case _:
                    pass

    def login(self):
        path = getUserDataPath() / "token.json"
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        self.creds = flow.run_local_server(port=0)
        
        with open(path, "w") as token:
            token.write(self.creds.to_json())

    def send(self, email, subject, content):
        if not self.creds:
            self.login()

        service = build("gmail", "v1", credentials=self.creds)

        content = f"<p>{content.replace("\n", "<br>")}</p>{SIGNATURE}"

        message = MIMEText(content, "html")
        message["To"] = email
        message["Subject"] = subject

        encoded = urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded}

        send = service.users().messages().send(userId="me", body=create_message).execute()
        debug(send)

    def receive(self):
        if not self.creds:
            self.login()

        service = build("gmail", "v1", credentials=self.creds)

        results = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()

        raw_messages = results.get("messages", [])

        batch = service.new_batch_http_request(callback=lambda req_id, msg, err: self.messages.append(Message.from_raw(msg)))

        ids = map(Message.id, self.messages)

        for message in raw_messages:
            if message["id"] in ids:
                debug(f'Id skipped: {message["id"]}')
                continue
            batch.add(service.users().messages().get(userId="me", id=message["id"], format='full'))

        batch.execute()
        return self.messages

if __name__ == "__main__":
    mail = MailManager()
    mail.login()
    mail.receive()