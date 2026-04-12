import json
from .utils import Singleton, getUserDataPath

def getContactsPath():
    return getUserDataPath() / "contacts.json"

class Contact():
    def __init__(self, initial=None):
        if initial==None:
            self.name = ""
            self.email = ""
        else:
            self.name = initial["name"]
            self.email = initial["email"]

class ContactsManager(metaclass=Singleton):
    def __init__(self):
        self.contactsPath = getContactsPath()
        if not self.contactsPath.exists():
            self.contactsPath.parent.mkdir(exist_ok=True)
            with open(self.contactsPath, 'w') as f:
                json.dump([], f)
        
        with open(self.contactsPath, "r") as f:
            self.contacts = list(map(Contact, json.load(f)))

    def getContacts(self):
        return self.contacts