from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

# all the helper lists
SUBJECTS = ["comp sci", "econ", "eng", "math", "bio"]
CONDITIONS = ["new", "used", "old"]
ROLES = ["seller", "buyer"]
ALL_ROLES = ROLES + ["admin"] # for the signup, so admins dont sign up but still is stored
OFFER_ACTIONS = ["accept", "accepted", "decline", "declined"]

def clean_text(value):
    if value is None:
        return value
    value = value.strip()
    if value == "":
        raise ValueError("cannot be blank")
    return value

# blueprints for all the query filters
# can be used in E1
class ListingSearch(BaseModel):
    subject: Optional[str] = None
    condition: Optional[str] = None
    max_price: Optional[int] = Field(default=None, gt=0)

    @field_validator("subject")
    @classmethod
    def valid_subject(cls, value):
        if value is not None and value not in SUBJECTS:
            raise ValueError("Invalid subject")
        return value

    @field_validator("condition")
    @classmethod
    def valid_condition(cls, value):
        if value is not None and value not in CONDITIONS:
            raise ValueError("Invalid condition")
        return value

# all the authetication blueprints
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class AccessToken(BaseModel):
    access_token: str

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
        if value not in ALL_ROLES:
            raise ValueError("Invalid user type")
        return value

class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

    @field_validator("username")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

class SignupRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=4)
    user_type: str

    @field_validator("username")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

    @field_validator("user_type")
    @classmethod
    def valid_user_type(cls, value):
        if value not in ROLES:
            raise ValueError("Invalid user type")
        return value


# blueprints for all the bodies passed in main
# can be used in E3
class ListingCreate(BaseModel):
    seller_roll: str = Field(min_length=1)
    title: str = Field(min_length=1)
    subject: str
    condition: str
    price: int = Field(ge=10, le=2000)

    @field_validator("seller_roll", "title")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

    @field_validator("subject")
    @classmethod
    def valid_subject(cls, value):
        if value not in SUBJECTS:
            raise ValueError("Invalid subject")
        return value

    @field_validator("condition")
    @classmethod
    def valid_condition(cls, value):
        if value not in CONDITIONS:
            raise ValueError("Invalid condition")
        return value

# can be used in E4
class PriceUpdate(BaseModel):
    seller_roll: str = Field(min_length=1)
    price: int = Field(ge=10, le=2000)

    @field_validator("seller_roll")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

# can be used in E6
class OfferCreate(BaseModel):
    listing_id: int = Field(gt=0)
    buyer_roll: str = Field(min_length=1)
    offer_price: int = Field(ge=1)

    @field_validator("buyer_roll")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

# can be used in E7
class OfferDecision(BaseModel):
    seller_roll: str = Field(min_length=1)
    action: str

    @field_validator("seller_roll")
    @classmethod
    def not_blank(cls, value):
        return clean_text(value)

    @field_validator("action")
    @classmethod
    def valid_action(cls, value):
        value = value.lower().strip()
        if value not in OFFER_ACTIONS:
            raise ValueError("Action must be 'accept' or 'decline'")
        return value


# all the response model blueprints
# can be used for signup in E5
class MessageOut(BaseModel):
    message: str

# can be used in E1, E3, E4, E8
class ListingOut(BaseModel):               # E1, E3, E4, E8
    id: int
    seller_roll: str
    title: str
    subject: str
    condition: str
    price: int
    listed_on: datetime
    status: str

# can be used for E2
class OfferSummary(BaseModel):
    id: int
    buyer_roll: str
    offer_price: int
    status: str
    offered_on: datetime

# for E2 this combines listingOut with the offers
class ListingDetailOut(ListingOut):
    offers: list[OfferSummary]

# use this for E9 to count the pending
class StudentListingOut(ListingOut):
    pending_offers: int

# can be used for E6 and E7
class OfferOut(BaseModel):
    id: int
    listing_id: int
    buyer_roll: str
    offer_price: int
    status: str
    offered_on: datetime

# can be used for E10
class StudentOfferOut(BaseModel):
    id: int
    listing_id: int
    title: str
    asking_price: int
    offer_price: int
    status: str
    offered_on: datetime
    