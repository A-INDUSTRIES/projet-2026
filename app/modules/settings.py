import json
from .utils import getUserDataPath, Singleton
from .logger import warn

def getSettingsPath():
    return getUserDataPath() / "settings.json"

class SettingsManager(metaclass=Singleton):
    def __init__(self):
        self.settingsPath = getSettingsPath()
        if not self.settingsPath.exists():
            self.settingsPath.parent.mkdir(exist_ok=True)
            with open(self.settingsPath, 'w') as f:
                json.dump({"fontSize": 24,
                           "animationSpeed": 1000,
                           "inputSpeed": 1000}, f)
        
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
                    value = 24
                if not value in [10, 18, 24, 32, 40]:
                    raise ValueError(f"The setting 'fontSize' can only take one of [10, 18, 24, 32, 40] as value, {value} was given.")
                self.settings[key] = value
                self.saveSettings()
            case "animationSpeed":
                if value==None:
                    value = 1000
                if not value in [500, 1000, 2000]:
                    raise ValueError(f"The setting 'animationSpeed' can only take one of [500, 1000, 2000] as value, {value} was given.")
                self.settings[key] = value
                self.saveSettings()
            case "inputSpeed":
                if value==None:
                    value = 1000
                if not value in [500, 1000, 2000]:
                    raise ValueError(f"The setting 'inputSpeed' can only take one of [500, 1000, 2000] as value, {value} was given.")
                self.settings[key] = value
                self.saveSettings()
    
    def saveSettings(self):
        with open(self.settingsPath, 'w') as f:
            json.dump(self.settings, f)