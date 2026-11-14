// the page to list a new book

import {useState} from "react";

const API_URL = "http://127.0.0.1:8001";

function SellPage({token, role}) {
  const [sellerRoll, setSellerRoll] = useState("");
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");
  const [condition, setCondition] = useState("");
  const [price, setPrice] = useState("");
  const [note, setNote] = useState(""); // the error or success message for this form

  // E3 adds a book to listing
  function addListing() {
    setNote("");
    fetch(API_URL + "/listings", {
      method: "POST",
      headers: {"Content-Type": "application/json", token: token},
      body: JSON.stringify({seller_roll: sellerRoll, title: title, subject: subject, condition: condition, price: Number(price)}),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.detail) {
          setNote(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
        } else {
          setNote("Book listed successfully!");
        }
      });
  }

  if (token === "") return <p>Please log in first.</p>;
  if (role !== "seller" && role !== "admin") return <p>Only sellers can list books.</p>;

  return (
    <>
      <h2>Sell a book</h2>
      <input placeholder="Roll number (Ex: 001)" value={sellerRoll} onChange={(e) => setSellerRoll(e.target.value)} />
      <input placeholder="Book title" value={title} onChange={(e) => setTitle(e.target.value)} />

      <select value={subject} onChange={(e) => setSubject(e.target.value)}>
        <option value="">Select subject</option>
        <option value="comp sci">comp sci</option>
        <option value="econ">econ</option>
        <option value="eng">eng</option>
        <option value="math">math</option>
        <option value="bio">bio</option>
      </select>

      <select value={condition} onChange={(e) => setCondition(e.target.value)}>
        <option value="">Select condition</option>
        <option value="new">new</option>
        <option value="used">used</option>
        <option value="old">old</option>
      </select>

      <input type="number" placeholder="Price (Max 2000)" value={price} onChange={(e) => setPrice(e.target.value)} />

      <p>{note}</p>

      <button onClick={addListing}>List book</button>
    </>
  );
}

export default SellPage;