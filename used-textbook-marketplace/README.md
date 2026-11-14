# Used Textbook Marketplace

**Team:** Aryan, Darsh, Samhita

## Problem Statement

Every year, seniors have textbooks they no longer need, while juniors spend a lot buying new ones, and there is no simple place on campus where the two can find each other. This project is a marketplace for that. A seller lists a book with their roll number, subject, condition and asking price. Buyers make offers, the seller accepts one offer (which reserves the book) and marks it sold after the hand-over. Only the seller can change the price, remove the listing or decide on offers, and there are no logins. It is built with a FastAPI + SQLite backend (port 8001) and a React frontend.

## Database

One SQLite file, `textbook.db`, with two tables:

- **listings:** id, seller_roll, title, subject, condition, price, listed_on, status
- **offers:** id, listing_id, buyer_roll, offer_price, status, offered_on

## API Endpoints Contribution

| # | What it does | Method | Path | Request body | Success code | Error codes | Who |
|:-:|:-------------|:------:|:-----|:-------------|:------------:|:------------|:---:|
| E1 | Browse available listings | GET | /listings?subject=&condition=&max_price= | none | 200 | 422 | Samhita |
| E2 | View one listing | GET | /listings/{listing_id} | none | 200 | 404 | Samhita |
| E3 | List a book | POST | /listings | seller_roll<br>title<br>subject<br>condition<br>price | 200 | 422 | Samhita |
| E4 | Change price | PATCH | /listings/{listing_id}/price | seller_roll<br>price | 200 | 400 (listing is not available)<br>403 (roll number is not seller's)<br>404 (listing id doesn't exist)<br>422 (price is not within range) | Samhita |
| E5 | Remove listing | DELETE | /listings/{listing_id} | seller_roll | 200 | 400 (listing is not available)<br>403 (roll number is not seller's)<br>404 (listing id doesn't exist)<br>422 (missing or empty roll number) | Aryan |
| E6 | Make an offer | POST | /offers | listing_id<br>buyer_roll<br>offer_price | 200 | 400 (offer on own listing, listing not available, second pending offer from same buyer)<br>404 (listing id doesn't exist)<br>422 (missing fields, offer price not between 1 and asking price) | Aryan |
| E7 | Accept/decline offer | PATCH | /offers/{offer_id} | seller_roll<br>action | 200 | 400 (offer is not pending, or listing not available)<br>403 (roll number is not seller's)<br>404 (offer id doesn't exist)<br>422 (missing fields, invalid action) | Aryan |
| E8 | Mark sold | PATCH | /listings/{listing_id}/sold | seller_roll | 200 | 400 (listing is not reserved)<br>403 (roll number is not seller's)<br>404 (listing id doesn't exist)<br>422 (missing or empty roll number) | Darsh |
| E9 | Student's listings | GET | /students/{roll_no}/listings | none | 200 | 404 (student roll number not found) | Darsh |
| E10 | Student's offers | GET | /students/{roll_no}/offers | none | 200 | 404 (student roll number not found) | Darsh |

## Frontend Contribution

| Member | Files | Endpoints | What they did |
|:---------:|:---------|:------------:|:-----------------|
| Samhita | App.jsx <br>SellBook.jsx<br>MyBooks.jsx | E1, E2, E3, E4 | Wrote the fetch functions for E1 to E4 in App.jsx <br>Built the Sell a book form (E3)<br>Built the My books dashboard |
| Aryan | App.jsx<br>index.css<br>App.css | E5, E6, E7 | Wrote the fetch functions for E5 to E7 in App.jsx (remove listing, make offer, accept/decline offer)<br>Designed and implemented the 2D retro pixel RPG aesthetic and styling |
| Darsh | App.jsx<br>BrowseListings.jsx<br>ListingCard.jsx | E8, E9, E10 (and E1, E6 through Browse Listing) | Wrote the fetch functions for E8 to E10 in App.jsx<br>Built the Browse listings page with its subject, condition and max price filters<br>Built the listing card with the Make offer boxes and button |

## How to Run

### Backend
1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy
   ```
3. Run the FastAPI server on port 8001:
   ```bash
   python -m uvicorn main:app --reload --port 8001
   ```
4. Access the API and interactive documentation:
   - Interactive Swagger UI: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
   - Alternative ReDoc: [http://127.0.0.1:8001/redoc](http://127.0.0.1:8001/redoc)

### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies and start the React dev server:
   ```bash
   npm install
   npm run dev
   ```

   ### Proof of work

Our App

1. Frontend

<img width="1920" height="1200" alt="Screenshot (2)" src="https://github.com/user-attachments/assets/b7c567a8-185b-48b3-984e-ec0ee5a13dfb" />


2. Backend
   
<img width="1920" height="1200" alt="Screenshot (3)" src="https://github.com/user-attachments/assets/903fae9a-0bd4-4765-8b65-0b88015518ca" />

