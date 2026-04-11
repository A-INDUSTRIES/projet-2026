import json, os
from pathlib import Path
from sys import platform
from .logging import warn

def getSettingsPath():
    """ Permet de récupérer le chemin du fichier de
    configuration en fonction du système.
    Pour l'instant le support s'étend à Windows et Linux
    """
    match platform:
        case "win32":
            path =  Path(os.environ["APPDATA"])
        case "linux":
            path =  Path.home() / ".config"
        case _:
            raise NotImplementedError(f"Settings for {platform} are not yet supported.")
    return path / "CommuniquerAvecLesYeux" / "settings.json"

class SettingsManager():
    def __init__(self):
        self.settingsPath = getSettingsPath()
        if not self.settingsPath.exists():
            self.settingsPath.parent.mkdir(exist_ok=True)
            with open(self.settingsPath, 'w') as f:
                json.dump({"fontSize": 16}, f)
        
        with open(self.settingsPath, "r") as f:
            self.settings = json.load(f)

    def getSetting(self, key):
        if not key in self.settings.keys():
            warn(f"The setting '{key}' does not exists, adding default value.")
            self.setSetting(key, None)
        return self.settings[key]
    
    def setSetting(self, key, value=None):
        match key:
            case "fontSize":
                if value==None:
                    value = 16
                if not value in [10, 12, 16, 20, 24]:
                    raise ValueError(f"The setting 'fontSize' can only take one of [10, 12, 16, 20, 24] as value, {value} was given.")
                self.settings[key] = value
                self.saveSettings()
    
    def saveSettings(self):
        with open(self.settingsPath, 'w') as f:
            json.dump(self.settings, f)