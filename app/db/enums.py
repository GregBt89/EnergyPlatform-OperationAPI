from enum import Enum

class AssetType(Enum):
    BESS = "BESS"
    ELY = "ELY"
    LOAD = "LOAD"
    FLEXLOAD = "FLEXLOAD"
    PVPP = "PVPP"
    WPP = "WPP"
    EVSTATION = "EVSTATION"
    OTHER = "OTHER"