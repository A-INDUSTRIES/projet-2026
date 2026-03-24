import json, os
from pathlib import Path
from sys import platform

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
                json.dump({"voice": 0}, f)
        
        with open(self.settingsPath, "r") as f:
            self.settings = json.load(f)

    def getSetting(self, key):
        if not key in self.settings.keys():
            raise KeyError(f"The setting '{key}' does not exists.\nThe following do: 'voice'")
        return self.settings[key]
    
    def setSetting(self, key, value):
        match key:
            case "voice":
                if not value in [0, 1]:
                    raise ValueError(f"The setting 'voice' can only take 0 or 1 as value, {value} was given.")
                self.settings[key] = value
                self.saveSettings()
    
    def saveSettings(self):
        with open(self.settingsPath, 'w') as f:
            json.dump(self.settings, f)