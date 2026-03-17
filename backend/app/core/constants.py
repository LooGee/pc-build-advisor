from enum import Enum


class ComponentCategory(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    MOTHERBOARD = "motherboard"
    RAM = "ram"
    STORAGE = "storage"
    PSU = "psu"
    CASE = "case"
    COOLER = "cooler"


class QuoteTier(str, Enum):
    MINIMUM = "minimum"
    BALANCED = "balanced"
    MAXIMUM = "maximum"


class PriceSource(str, Enum):
    DANAWA = "danawa"
    COMPUZONE = "compuzone"
    COUPANG = "coupang"
    PCPARTPICKER = "pcpartpicker"


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


# CPU Socket -> Compatible Chipsets
SOCKET_CHIPSET_MAP = {
    "LGA1700": ["Z790", "B760", "H770", "H710"],
    "LGA1851": ["Z890", "B860", "H810"],
    "AM5": ["X870E", "X870", "B850", "X670E", "X670", "B650E", "B650"],
    "AM4": ["X570", "B550", "B450", "X470", "B350"],
}

# Radiator sizes
RADIATOR_SIZES = ["120mm", "240mm", "280mm", "360mm", "420mm"]
