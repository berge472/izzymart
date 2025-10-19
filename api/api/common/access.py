from enum import Enum

class Access(str, Enum):
    public = "public"       #All users can access
    private = "private"     #Only owner can access
    readOnly = "read-only"   #All users can access, but only owner can modify