import json
from .utils import Singleton, getUserDataPath

def getContactsPath():
    return getUserDataPath() / "contacts.json"

class Contact():
    def __init__(self, initial=None, name="", email=""):
        if initial==None:
            self.name = name
            self.email = email
        else:
            self.name = initial["name"]
            self.email = initial["email"]

class ContactDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def decode(self, s, **kwargs):
        data = super().decode(s, **kwargs)
        return {int(k): Contact(v) if isinstance(v, dict) and "name" in v else v for k, v in data.items()}
    
class ContactEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def default(self, o):
        if isinstance(o, Contact):
            return {"name": o.name, "email": o.email}
        return super().default(o)

class ContactsManager(metaclass=Singleton):
    def __init__(self):
        self.contactsPath = getContactsPath()
        if not self.contactsPath.exists():
            self.contactsPath.parent.mkdir(exist_ok=True)
            with open(self.contactsPath, 'w') as f:
                json.dump({}, f, indent=4)
        
        with open(self.contactsPath, "r") as f:
            self.contacts = json.load(f, cls=ContactDecoder)

    def getContacts(self):
        return self.contacts
    
    def createContact(self, contact):
        self.contacts[max([-1] + list(self.contacts.keys()))+1] = contact
        self.save()

    def editContact(self, id, contact):
        self.contacts[id] = contact
        self.save()

    def deleteContact(self, id):
        self.contacts.pop(id)
        self.save()

    def save(self):
        with open(self.contactsPath, 'w') as f:
            json.dump(self.contacts, f, indent=4, cls=ContactEncoder)