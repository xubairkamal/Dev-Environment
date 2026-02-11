from enum import Enum

class DBErrorCodes(Enum):
    CONCURRENCY_VIOLATION = 50001
    RECORD_NOT_FOUND = 50002
    DATABASE_CONNECTION_ERROR = 10001
    UNKNOWN_ERROR = 99999

class PermissionType(Enum):
    CAN_VIEW = "CanView"
    CAN_CREATE = "CanCreate"
    CAN_EDIT = "CanEdit"
    CAN_DELETE = "CanDelete"