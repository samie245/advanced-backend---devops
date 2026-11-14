import {useState, useEffect} from "react";
import ListingCard from "./ListingCard";

const API_URL = "http://127.0.0.1:8001";

function BrowsePage({token, role}) {
  const [listings, setListings] = useState([]);
  const [subject, setSubject] = useState("");
  const [condition, setCondition] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [note, setNote] = useState(""); // the error message for the search

  // only buyers (and admin) can make offers
  const canOffer = role === "buyer" || role === "admin";

  // E1 gets all listings along with the url filters
  function getListings() {
    setNote("");
    const subjectFilter = subject ? "subject=" + subject + "&" : "";
    const conditionFilter = condition ? "condition=" + condition + "&" : "";
    const priceFilter = maxPrice ? "max_price=" + maxPrice : "";

    fetch(API_URL + "/listings?" + subjectFilter + conditionFilter + priceFilter, {
      headers: {token: token},
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          setListings(data);
        }
      });
  }

  // E1 shows all listings when the page loads, but only once logged in
  useEffect(() => {
    if (token !== "") getListings();
  }, [token]);

  // E6 junior makes an offer, setCardNote is that card's own message
  function makeOffer(listingId, buyerRoll, offerPrice, setCardNote) {
    setCardNote("");
    fetch(API_URL + "/offers", {
      method: "POST",
      headers: {"Content-Type": "application/json", token: token},
      body: JSON.stringify({listing_id: listingId, buyer_roll: buyerRoll, offer_price: Number(offerPrice)}),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setCardNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          setCardNote("Offer placed successfully!");
        }
      });
  }

  if (token === "") return <p>Please log in first.</p>;

  return (
    <>
      <h2>Browse listings</h2>

      <select value={subject} onChange={(e) => setSubject(e.target.value)}>
        <option value="">All subjects</option>
        <option value="comp sci">comp sci</option>
        <option value="econ">econ</option>
        <option value="eng">eng</option>
        <option value="math">math</option>
        <option value="bio">bio</option>
      </select>

      <select value={condition} onChange={(e) => setCondition(e.target.value)}>
        <option value="">All conditions</option>
        <option value="new">new</option>
        <option value="used">used</option>
        <option value="old">old</option>
      </select>

      <input type="number" placeholder="Max price" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />
      <p>{note}</p>
      <button onClick={getListings}>Search</button>

      <ul className="products">
        {listings.map((listing) => (
          <ListingCard key={listing.id} listing={listing} makeOffer={makeOffer} canOffer={canOffer} />
        ))}
      </ul>
    </>
  );
}

export default BrowsePage;