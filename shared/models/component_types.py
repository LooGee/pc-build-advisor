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


class StorageType(str, Enum):
    NVME = "NVMe"
    SATA_SSD = "SATA_SSD"
    HDD = "HDD"


class CoolerType(str, Enum):
    AIR = "air"
    AIO_120 = "aio_liquid_120"
    AIO_240 = "aio_liquid_240"
    AIO_280 = "aio_liquid_280"
    AIO_360 = "aio_liquid_360"
    CUSTOM_LOOP = "custom_loop"


class FormFactor(str, Enum):
    E_ATX = "E-ATX"
    ATX = "ATX"
    MATX = "mATX"
    ITX = "ITX"


class PsuFormFactor(str, Enum):
    ATX = "ATX"
    SFX = "SFX"
    SFX_L = "SFX-L"
