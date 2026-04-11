import json
from .utils import Singleton, getUserDataPath

def getContactsPath():
    return getUserDataPath() / "contacts.json"

class ContactsManager(metaclass=Singleton):
    def __init__(self):
        pass