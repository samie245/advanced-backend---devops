import {useState} from "react";

const API_URL = "http://127.0.0.1:8001";

function MyBooksPage() {
  const [rollNo, setRollNo] = useState("");
  const [newPrice, setNewPrice] = useState("");
  const [myListings, setMyListings] = useState([]);
  const [myOffers, setMyOffers] = useState([]);
  const [listing, setListing] = useState([]);

  // message is only for the background reloads (refreshes after an action)
  const [message, setMessage] = useState("");

  // each note is the error or success message that shows next to its own buttons
  const [showNote, setShowNote] = useState("");   // roll number box, Show and View offers
  const [priceNote, setPriceNote] = useState(""); // new price box and Save
  const [bookNote, setBookNote] = useState("");   // Mark sold and Remove
  const [offerNote, setOfferNote] = useState(""); // Accept and Decline

  // E2 takes listing id and gets specific listing
  function getListing(id, setNote) {
    setNote("");
    fetch(API_URL + "/listings/" + id)
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          setListing([data]);
        }
      });
  }

  // E4 changes the price of a book on listing
  function changePrice(id, sellerRoll, price, setNote) {
    setNote("");
    fetch(API_URL + "/listings/" + id + "/price", {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({seller_roll: sellerRoll, price: price}),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          setNote("Price updated successfully!");
          getListing(id, setMessage);
          getMyListings(sellerRoll, setMessage);
        }
      });
  }

  // E5 deletes the listing
  function removeListing(id, sellerRoll, setNote) {
    setNote("");
    fetch(API_URL + "/listings/" + id + "?seller_roll=" + sellerRoll, {
      method: "DELETE",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          getMyListings(sellerRoll, setMessage);
          setListing([]);
        }
      });
  }

  // E7 seller accepts or declines an offer
  function decideOffer(offerId, sellerRoll, action, listingId, setNote) {
    setNote("");
    fetch(API_URL + "/offers/" + offerId, {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({seller_roll: sellerRoll, action: action}),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          setNote("Offer updated!");
          getMyListings(sellerRoll, setMessage);
          if (listingId) getListing(listingId, setMessage);
        }
      });
  }

  // E8 marks a listing sold
  function markSold(listingId, sellerRoll, setNote) {
    setNote("");
    fetch(API_URL + "/listings/" + listingId + "/sold?seller_roll=" + sellerRoll, { method: "PATCH" })
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          setNote("Marked as sold!");
          getMyListings(sellerRoll, setMessage);
          getListing(listingId, setMessage);
        }
      });
  }

  // E9 gets one student's listings, each with its number of pending offers
  function getMyListings(rollNo, setNote) {
    fetch(API_URL + "/students/" + rollNo + "/listings")
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          setMyListings(data);
        }
      });
  }

  // E10 gets one student's offers, each with the book's title and asking price
  function getMyOffers(rollNo, setNote) {
    fetch(API_URL + "/students/" + rollNo + "/offers")
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          setMyOffers(data);
        }
      });
  }

  // E9 + E10 used by the Show button
  function showMyBooks(rollNo, setNote) {
    if (rollNo === "") {
      setNote("Enter a roll number");
    } else {
      setNote("");
      getMyListings(rollNo, setNote);
      getMyOffers(rollNo, setNote);
    }
  }

  return (
    <>
      <h2>My books</h2>
      {message && <p className="message">{message}</p>}
      <input placeholder="Roll number (Ex : 001)" value={rollNo} onChange={(e) => setRollNo(e.target.value)} />
      <button onClick={() => showMyBooks(rollNo, setShowNote)}>Show</button>
      <p>{showNote}</p>

      <h3>My listings</h3>
      {myListings.map((item) => (
        <div key={item.id}>
          <p>{item.title} | ₹{item.price} | {item.status} | Pending offers: {item.pending_offers}</p>
          <button onClick={() => getListing(item.id, setShowNote)}>View offers</button>
        </div>
      ))}

      {listing.map((book) => (
        <div key={book.id}>
          <hr />
          <h3>{book.title}</h3>
          <p>₹{book.price} | {book.status}</p>

          <input type="number" placeholder="New price (Max 2000)" value={newPrice} onChange={(e) => setNewPrice(e.target.value)} />
          <button onClick={() => changePrice(book.id, rollNo, newPrice * 1, setPriceNote)}>Save</button>
          <p>{priceNote}</p>

          <button onClick={() => markSold(book.id, rollNo, setBookNote)}>Mark sold</button>
          <button onClick={() => removeListing(book.id, rollNo, setBookNote)}>Remove</button>
          <p>{bookNote}</p>

          <h4>Offers</h4>
          <p>{offerNote}</p>
          {book.offers.map((offer) => (
            <div key={offer.id} className={offer.status}>
              <p>{offer.buyer_roll} offered ₹{offer.offer_price} ({offer.status})</p>
              <button onClick={() => decideOffer(offer.id, rollNo, "accept", book.id, setOfferNote)}>Accept</button>
              <button onClick={() => decideOffer(offer.id, rollNo, "decline", book.id, setOfferNote)}>Decline</button>
            </div>
          ))}
          <hr />
        </div>
      ))}

      <h3>My offers</h3>
      {myOffers.map((offer) => (
        <p key={offer.id}>{offer.title} | Asking ₹{offer.asking_price} | My offer ₹{offer.offer_price} | {offer.status}</p>
      ))}
    </>
  );
}

export default MyBooksPage;