import { useState } from "react";

function ListingCard({ listing, makeOffer, canOffer }) {
  const [buyerRoll, setBuyerRoll] = useState("");
  const [offerPrice, setOfferPrice] = useState("");
  const [note, setNote] = useState(""); // the error or success message for this card's offer

  return (
    <li className="product">
      <h2>{listing.title}</h2>
      <p>₹{listing.price}</p>
      <p>Subject: {listing.subject}</p>
      <p>Condition: {listing.condition}</p>
      <p>Seller: {listing.seller_roll}</p>

      {canOffer && (
        <>
          <h3>Make offer</h3>
          <input placeholder="Roll number (Ex: 001)" value={buyerRoll} onChange={(e) => setBuyerRoll(e.target.value)} />
          <input placeholder="Offer price (1 - LP)" value={offerPrice} onChange={(e) => setOfferPrice(e.target.value)} />
          <p>{note}</p>
          <button onClick={() => makeOffer(listing.id, buyerRoll, offerPrice, setNote)}>Make offer</button>
        </>
      )}
    </li>
  );
}

export default ListingCard;