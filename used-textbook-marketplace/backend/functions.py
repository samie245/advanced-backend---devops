from sqlalchemy import Integer, String, Column, DateTime, create_engine
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt 
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from models import TokenPayload

DB_PATH = "textbook.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

ADMIN_USERNAME = "drdoofenshmirtz"
ADMIN_PASSWORD = "perrytheplatypus"
ACCESS_TOKEN_EXPIRY = 15 # expires after that many mins
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 # 7 days in mins
SECRET_KEY = "phineas-and-ferb"
ALGORITHM = "HS256"

ph = PasswordHasher()

class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True)
    user_type = Column(String)
    username = Column(String)
    password = Column(String)


subjects = ["comp sci", "econ", "eng", "math", "bio"]
conditions = ["new", "used", "old"]

class Listing(Base):
    __tablename__ = "listings"  
    id = Column(Integer, primary_key=True)
    seller_roll = Column(String)
    title = Column(String)
    subject = Column(String)
    condition = Column(String)
    price = Column(Integer)
    listed_on = Column(DateTime, default=datetime.now)
    status = Column(String)


class Offer(Base):
    __tablename__ = "offers"
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer)
    buyer_roll = Column(String)
    offer_price = Column(Integer)
    status = Column(String)
    offered_on = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)

def convert_dict(listing):
    return {
        "id": listing.id,
        "seller_roll": listing.seller_roll,
        "title": listing.title,
        "subject": listing.subject,
        "condition": listing.condition,
        "price": listing.price,
        "listed_on": listing.listed_on,
        "status": listing.status,
    }

def convert_offer_dict(offer): 
    return {
        "id": offer.id,
        "listing_id": offer.listing_id,
        "buyer_roll": offer.buyer_roll,
        "offer_price": offer.offer_price,
        "status": offer.status,
        "offered_on": offer.offered_on,
    }

# E1 gets available listings
def get_listings(subject=None, condition=None, max_price=None):
    session = Session(engine)
    result = []
    for listing in session.query(Listing).all():
        if listing.status == "available":
            result.append(convert_dict(listing))
    session.close()

    if subject is not None:
        by_subject = []
        for item in result:
            if item["subject"] == subject:
                by_subject.append(item)
        result = by_subject

    if condition is not None:
        by_condition = []
        for item in result:
            if item["condition"] == condition:
                by_condition.append(item)
        result = by_condition

    if max_price is not None:
        by_price = []
        for item in result:
            if item["price"] <= max_price:
                by_price.append(item)
        result = by_price

    return result


# E2 gets one listing based on id
def get_listing(listing_id):
    session = Session(engine)
    listing = session.get(Listing, listing_id)
    if listing is None:
        session.close()
        return None

    data = convert_dict(listing)
    data["offers"] = []
    for offer in session.query(Offer).all():
        if offer.listing_id == listing_id:
            data["offers"].append({
                "id": offer.id,
                "buyer_roll": offer.buyer_roll,
                "offer_price": offer.offer_price,
                "status": offer.status,
                "offered_on": offer.offered_on,
            })
    session.close()
    return data

# E3 list a book 
def add_listing(seller_roll, title, subject, condition, price):
    session = Session(engine)
    listing = Listing(
        seller_roll=seller_roll,
        title=title,
        subject=subject,
        condition=condition,
        price=price,
        status="available"
    )
    session.add(listing)
    session.commit()
    data = convert_dict(listing)
    session.close()
    return data


# E4 change a listings price
def update_price(listing_id, new_price):
    session = Session(engine)
    listing = session.get(Listing, listing_id)
    if listing is None:
        session.close()
        return None
    listing.price = new_price
    session.commit()
    data = convert_dict(listing)
    session.close()
    return data



# E5 remove a listing
def delete_listing(listing_id):
    session = Session(engine)
    listing = session.get(Listing, listing_id)
    if listing is not None:
        for offer in session.query(Offer).filter(Offer.listing_id == listing_id).all():
            session.delete(offer)
        session.delete(listing)
        session.commit()
    session.close()
    return {"message": "Listing removed successfully"}


# E6 helper funct to check if this kid already sent an offer and is spamming
def has_pending_offer(listing_id, buyer_roll):
    session = Session(engine)
    existing = session.query(Offer).filter(
        Offer.listing_id == listing_id,
        Offer.buyer_roll == buyer_roll,
        Offer.status == "pending"
    ).first()
    session.close()
    return existing is not None


# E6 drops the offer into the db and hopes for the best
def add_offer(listing_id, buyer_roll, offer_price):
    session = Session(engine)
    offer = Offer(
        listing_id=listing_id,
        buyer_roll=buyer_roll,
        offer_price=offer_price,
        status="pending",
        offered_on=datetime.now()
    )
    session.add(offer)
    session.commit()
    data = convert_offer_dict(offer)
    session.close()
    return data


# E7 quick peek to grab the offer details
def get_offer(offer_id):
    session = Session(engine)
    offer = session.get(Offer, offer_id)
    if offer is None:
        session.close()
        return None
    data = convert_offer_dict(offer)
    session.close()
    return data


# E7 seals the deal or shatters the junior's dreams
def update_offer_status(offer_id, action):
    session = Session(engine)
    offer = session.get(Offer, offer_id)
    if offer is None:
        session.close()
        return None

    if action in ["accept", "accepted"]:
        offer.status = "accepted"
        listing = session.get(Listing, offer.listing_id)
        if listing:
            listing.status = "reserved"

        other_offers = session.query(Offer).filter(
            Offer.listing_id == offer.listing_id,
            Offer.id != offer.id,
            Offer.status == "pending"
        ).all()
        for other in other_offers:
            other.status = "declined"
    else:
        offer.status = "declined"

    session.commit()
    data = convert_offer_dict(offer)
    session.close()
    return data



# E8 mark a listing sold
def mark_sold(listing_id):
    session = Session(engine)
    listing = session.get(Listing, listing_id)
    if listing is None:
        session.close()
        return None
    listing.status = "sold"
    session.commit()
    data = convert_dict(listing)
    session.close()
    return data


# E9 get one student's listings, each with its number of pending offers
def get_student_listings(roll_no):
    session = Session(engine)
    result = []
    for listing in session.query(Listing):
        if listing.seller_roll == roll_no:
            data = convert_dict(listing)

            pending = 0
            for offer in session.query(Offer):
                if offer.listing_id == listing.id and offer.status == "pending":
                    pending = pending + 1
            data["pending_offers"] = pending

            result.append(data)
    session.close()
    return result


# E10 get one student's offers, each with the book's title and asking price
def get_student_offers(roll_no):
    session = Session(engine)
    result = []
    for offer in session.query(Offer):
        if offer.buyer_roll == roll_no:
            listing = session.get(Listing, offer.listing_id)
            if listing is not None:
                result.append({
                    "id": offer.id,
                    "listing_id": offer.listing_id,
                    "title": listing.title,
                    "asking_price": listing.price,
                    "offer_price": offer.offer_price,
                    "status": offer.status,
                    "offered_on": offer.offered_on,
                })
    session.close()
    return result

# implementing jwt tokens
# verifying login 
def verify_login(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        access_token = create_token(user_id=0, user_type="admin", username=username, token_type="access")
        refresh_token = create_token(user_id=0, user_type="admin", username=username, token_type="refresh")
        return {"access_token": access_token, "refresh_token": refresh_token}
    session = Session(engine)
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False
    user_id = user.user_id
    user_type = user.user_type
    session.close()
    access_token = create_token(user_id=user_id, user_type=user_type, username=username, token_type="access")
    refresh_token = create_token(user_id=user_id, user_type=user_type, username=username, token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token}

# creating jwt token
def create_token(user_id, user_type, username, token_type):
    time = ACCESS_TOKEN_EXPIRY # takes it as access token default, if its refresh, it changes
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY    
    payload = {
        "user_id": user_id,
        "user_type":user_type,
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

# verifying token
def verify_token(token, token_type="access"):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        data = TokenPayload.model_validate(payload)
    except:
        return False
    
    if  data.token_type == token_type:
        return data
    return False

# registering a user
def register_user(username: str, password: str, user_type: str):
    session = Session(engine)
    user_exists = session.query(User).filter_by(username=username).first()
    if user_exists is not None or username == ADMIN_USERNAME:
        session.close()
        return False
    user_exists = session.query(User).filter_by(username=username).first()
    if user_exists is not None:
        session.close()
        return False
    
    session.add(User(username=username, password=ph.hash(password), user_type=user_type))
    session.commit()
    session.close()
    return True

# controlling authorizaton 
def authenticate_role(user_type, roles):
    if user_type in roles: 
        return True
    return False
