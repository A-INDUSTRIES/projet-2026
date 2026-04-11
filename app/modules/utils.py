import os
from pathlib import Path
from sys import platform

# https://stackoverflow.com/questions/6760685/what-is-the-best-way-of-implementing-a-singleton-in-python
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def getUserDataPath():
    match platform:
        case "win32":
            path =  Path(os.environ["APPDATA"])
        case "linux":
            path =  Path.home() / ".config"
        case _:
            raise NotImplementedError(f"{platform} is not yet supported.")
    return path / "CommuniquerAvecLesYeux"