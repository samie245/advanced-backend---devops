import {useState} from "react";

const API_URL = "http://127.0.0.1:8001";

function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [userType, setUserType] = useState("buyer");
  const [message, setMessage] = useState("");

  // registers a user
  async function register() {
    const res = await fetch(API_URL + "/signup", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({username: username, password: password, user_type: userType}),
    });
    const data = await res.json();

    if (data.detail) {
      setMessage(typeof data.detail === "string" ? data.detail : data.detail[0].msg);
    } else {
      setMessage(data.message);
    }
  }

  return (
    <>
      <h2>Register</h2>
      <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <select value={userType} onChange={(e) => setUserType(e.target.value)}>
        <option value="buyer">Buyer</option>
        <option value="seller">Seller</option>
      </select>
      <button onClick={register}>Register</button>
      <p>{message}</p>
    </>
  );
}

export default RegisterPage;