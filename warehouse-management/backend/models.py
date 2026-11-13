from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional
from datetime import date, datetime


# helper class that holds blueprint of blank error and cleaned values using strip
# for this we import feild_validator
def clean_text(value):
    if value is None: # PackageUpdate fields can be None
        return value
    value = value.strip()
    if value == "":
        raise ValueError("cannot be blank")
    return value

# used in E1, E8 and login to remove all the function feilds and httpexceptions and put them as part of basemodel requirements
# for this we imported basemodel and feild
class PackageCreate(BaseModel):
    name: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    weight: int = Field(gt=0)
    
    @field_validator("name", "destination")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

class DispatchBatchCreate(BaseModel):
    destination: str = Field(min_length=1)
    vehicle_number: int = Field(gt=0)
    
    @field_validator("destination")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

class LoginRequest(BaseModel):
    username: str
    password: str
    
# used in E3 for removing all the func feilds and to handle all httpexceptions here
# for this we imported model_validator and optional form typing
class PackageUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    destination: Optional[str] = Field(default=None, min_length=1)
    weight: Optional[int] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def something_to_update(self):
        if self.name is None and self.destination is None and self.weight is None:
            raise ValueError("Nothing to update")
        return self
    
    @field_validator("name", "destination")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)
    
# used in E5 and E6 to validate the package search by calling the model inside the endpoint for the path params
# for this we imported date from datetime   
class PackageSearch(BaseModel):
    destination: Optional[str] = None
    status: Optional[str] = None
    arrival_date: Optional[date] = None # "2026-11-12" becomes a date, a bad string fails

    @field_validator("status")
    @classmethod
    def valid_status(cls, value):
        if value is not None and value not in ["Registered", "Dispatched"]:
            raise ValueError("Invalid status")
        return value
    
class DispatchBatchSearch(BaseModel):
    destination: Optional[str] = None
    vehicle_number: Optional[int] = None   # "1234" becomes 1234, "abc" fails
    dispatch_status: Optional[str] = None

    @field_validator("dispatch_status")
    @classmethod
    def valid_dispatch_status(cls, value):
        if value is not None and value not in ["Pending", "Dispatched"]:
            raise ValueError("Invalid dispatch status")
        return value


# used in E2, E5 and login, bec these functions give an obj output for display, so 
# we changed the decorators and defined a "response_model", so only feilds in the model are sent or its 500 error
# for this we imported datetime
# package out replaces what our convert to dict helper function in main.py did
class PackageOut(BaseModel):
    package_id: int
    name: str
    destination: str
    weight: int
    arrival_date: datetime
    status: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


# used in functions.py where we changed the verifytoken function 
class TokenPayload(BaseModel):
    user_id: int
    user_type: str
    username: str
    token_type: str

    @field_validator("token_type")
    @classmethod
    def valid_token(cls, value):
        if value not in ["access", "refresh"]:
            raise ValueError("Invalid token type")
        return value
    
    @field_validator("user_type")
    @classmethod
    def valid_user(cls, value):
        if value not in ["admin", "delivery_partner", "customer"]:
            raise ValueError("Invalid user type")
        return value
    
# used in registering a user (works the same as token payload)
ROLES = ["delivery_partner", "customer"]
class SignupRequest(BaseModel):
    username: str
    password: str
    user_type: str

    @field_validator("user_type")
    @classmethod
    def valid_user_type(cls, value):
        if value not in ROLES:
            raise ValueError("Invalid user type")
        return value