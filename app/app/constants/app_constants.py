from app.logs.logging import Levels, LogTypes

#App Related
APP_NAME = "app"
SOFTWARE_NAME = "CardioNet"
SOFTWARE_DESCRIPTION = "GRU-Based Cardiac Arrhythmia Detection System"

#Database Related
EXCEPT_MODELS = [
    "LogEntry",
    "Permission",
    "Group",
    #"User",
    "ContentType",
    "Session",
]

# Permission Related
TOKEN_HAS_EXPIRY = False
TOKEN_VALIDITY = 60 * 60

# Logging Related
LOG_LEVEL = Levels()
LOG_TYPE = LogTypes()
HAS_LOGGING = False
IS_DATABASE_LOGGING = False

# Styling Related
THEMES = None

# Dataset Related
SECONDS = 30
SAMPLES_TO_LOAD = 8
EPOCHS = 5

# Sensor Related Analog Values
MINIMUM_VALUE = 1
MAXIMUM_VALUE = 650
SAMPLING_FREQUENCY = 100




