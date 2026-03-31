_level = 0

levels = {
    "critical": 0,
    "warning": 1,
    "info": 2,
    "debug": 3
}

def setLogLevel(level: str):
    global _level
    _level = levels[level]

def error(message: str):
    print(f"\033[1;31mERROR: {message}\033[0m")

def warn(message: str):
    if _level >= 1:
        print(f"\033[0;33mWARN: {message}\033[0m")

def info(message: str):
    if _level >= 2:
        print(f"\033[0;32mINFO: {message}\033[0m")

def debug(message: str):
    if _level >= 3:
        print(f"\033[0;36mDEBUG: {message}\033[0m")