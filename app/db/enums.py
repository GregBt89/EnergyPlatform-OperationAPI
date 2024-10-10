from enum import Enum

class UserType(Enum):
    ADMIN = "ADMIN"
    AGGREGATOR = "AGGREGATOR"
    CLIENT = "CLIENT"

class SendInvoice(Enum):
    POST = "POST"
    EMAIL = "EMAIL"

class PaymentMethod(Enum):
    DEBIT = "DEBIT"
    TRANSFER = "TRANSFER"

class MeterType(Enum):
    MAIN = "MAIN"
    SUB = "SUB-METER"
    RTU = "RTU"
    PMU = "PMU"
    PLC = "PLC"

class PODType(Enum):
    PRODUCTION = "PRODUCTION"
    CONSUMPTION = "CONSUMPTION"

class ECType(Enum):
    ACR = "ACR"
    CEL = "CEL"
    APS = "APS"
    CEN = "CEN"
    CER = "CER"

class ECStatus(Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    DISSOLVED = "DISSOLVED"
    DELETED = "DELETED"

class ClientType(Enum):
    INDUSTRIAL = "INDUSTRIAL"
    COMMERCIAL = "COMMERCIAL"
    RESIDENTIAL = "RESIDENTIAL"

class OperatorRole(Enum):
    DSO = "DSO"
    TSO = "TSO"

class VoltageLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AssetType(Enum):
    BESS = "BESS"
    ELY = "ELY"
    LOAD = "LOAD"
    FLEXLOAD = "FLEXLOAD"
    PVPP = "PVPP"
    WPP = "WPP"
    EVSTATION = "EVSTATION"
    HYDRO = "HYDRO"
    OTHER = "OTHER"