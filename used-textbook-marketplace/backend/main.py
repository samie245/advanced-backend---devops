from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import functions
from models import (
    LoginRequest, SignupRequest, TokenPair, AccessToken, MessageOut,
    ListingCreate, PriceUpdate, OfferCreate, OfferDecision, ListingSearch,
    ListingOut, ListingDetailOut, StudentListingOut,
    OfferOut, StudentOfferOut,
)

app = FastAPI(
    title = "Used Textbook Marketplace API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# E1 gets available listings
@app.get("/listings", response_model=list[ListingOut])
def browse_listings(subject=None, condition=None, max_price=None):
    try:
        filters = ListingSearch(subject=subject, condition=condition, max_price=max_price)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors()[0]["msg"])
    return functions.get_listings(subject=filters.subject, condition=filters.condition, max_price=filters.max_price)

# E2 gets one listing with its offers
@app.get("/listings/{listing_id}", response_model=ListingDetailOut)
def view_listing(listing_id: int):
    listing = functions.get_listing(listing_id=listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

# E3 lists a book
@app.post("/listings", response_model=ListingOut)
def create_listing(listing: ListingCreate):
    return functions.add_listing(
        seller_roll=listing.seller_roll,
        title=listing.title,
        subject=listing.subject,
        condition=listing.condition,
        price=listing.price,
    )

# E4 changes a listing's price
@app.patch("/listings/{listing_id}/price", response_model=ListingOut)
def change_price(listing_id: int, update: PriceUpdate):
    listing = functions.get_listing(listing_id=listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing["seller_roll"] != update.seller_roll:
        raise HTTPException(status_code=403, detail="Only seller can change the price")
    if listing["status"] != "available":
        raise HTTPException(status_code=400, detail="You can only change the price of an available book")
    return functions.update_price(listing_id=listing_id, new_price=update.price)


# E5 yeets the listing out of existence so juniors stop dm'ing the seller
@app.delete("/listings/{listing_id}", response_model=MessageOut)
def remove_listing(listing_id: int, seller_roll: str = None):
    if not seller_roll:
        raise HTTPException(status_code=422, detail="Seller roll is required")
    listing = functions.get_listing(listing_id=listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing["seller_roll"] != seller_roll:
        raise HTTPException(status_code=403, detail="You're not allowed to do this")
    if listing["status"] != "available":
        raise HTTPException(status_code=400, detail="Cannot remove a listing that is not available")
    return functions.delete_listing(listing_id=listing_id)


# E6 broke junior attempts to bargain for their degree
@app.post("/offers", response_model=OfferOut)
def make_offer(offer: OfferCreate):
    listing = functions.get_listing(listing_id=offer.listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if offer.offer_price > listing["price"]:
        raise HTTPException(status_code=422, detail="An offer price must be between 1 and the asking price")
    if listing["seller_roll"] == offer.buyer_roll:
        raise HTTPException(status_code=400, detail="You can't make an offer on your own book")
    if listing["status"] != "available":
        raise HTTPException(status_code=400, detail="Listing is not available")
    if functions.has_pending_offer(listing_id=offer.listing_id, buyer_roll=offer.buyer_roll):
        raise HTTPException(status_code=400, detail="You already have a pending offer on this listing")
    return functions.add_offer(listing_id=offer.listing_id, buyer_roll=offer.buyer_roll, offer_price=offer.offer_price)


# E7 seller either secures the bag or tells the junior to touch grass
@app.patch("/offers/{offer_id}", response_model=OfferOut)
def decide_offer(offer_id: int, decision: OfferDecision):
    offer = functions.get_offer(offer_id=offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")

    listing = functions.get_listing(listing_id=offer["listing_id"])
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing["seller_roll"] != decision.seller_roll:
        raise HTTPException(status_code=403, detail="You're not allowed to do this")

    if offer["status"] != "pending":
        raise HTTPException(status_code=400, detail="Offer is not pending")

    if decision.action in ["accept", "accepted"] and listing["status"] != "available":
        raise HTTPException(status_code=400, detail="Listing is not available")

    return functions.update_offer_status(offer_id=offer_id, action=decision.action)


# E8 marks a listing sold
@app.patch("/listings/{listing_id}/sold", response_model=ListingOut)
def mark_listing_sold(listing_id: int, seller_roll=None):
    listing = functions.get_listing(listing_id=listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not seller_roll:
        raise HTTPException(status_code=422, detail="Missing seller roll number")
    if listing["seller_roll"] != seller_roll:
        raise HTTPException(status_code=403, detail="Only seller can mark the book sold")
    if listing["status"] != "reserved":
        raise HTTPException(status_code=400, detail="Only a reserved book can be marked sold")
    return functions.mark_sold(listing_id=listing_id)


# E9 gets one student's listings with their number of pending offers
@app.get("/students/{roll_no}/listings", response_model=list[StudentListingOut])
def student_listings(roll_no: str):
    return functions.get_student_listings(roll_no=roll_no)


# E10 gets one student's offers with the book's title and asking price
@app.get("/students/{roll_no}/offers", response_model=list[StudentOfferOut])
def student_offers(roll_no: str):
    return functions.get_student_offers(roll_no=roll_no)


# verify login
@app.post("/login", response_model=TokenPair)
def login(creds: LoginRequest):
    token = functions.verify_login(username=creds.username, password=creds.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token

# refresh token
@app.post(path="/refresh", response_model=AccessToken)
def refresh(refresh_token = Header(None)):
    user = functions.verify_token(token=refresh_token, token_type="refresh")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or Expired refresh token")
    access_token = functions.create_token(user_id=user.user_id, user_type=user.user_type, username=user.username, token_type="access")
    return {"access_token": access_token}


# registers a user, admin is not allowed here because the admin is hard coded
@app.post(path="/signup", response_model=MessageOut)
def register_user(creds: SignupRequest):
    if functions.register_user(username=creds.username, password=creds.password, user_type=creds.user_type):
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=400, detail="User already exists")