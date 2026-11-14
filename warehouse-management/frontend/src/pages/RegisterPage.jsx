import {useState} from "react";


function RegisterPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [userType, setUserType] = useState("customer");
    const [message, setMessage] = useState("");

    // registers a user
    async function register() {
        const res = await fetch("http://localhost:8001/signup", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username: username, password: password, user_type: userType})
        });
        const data = await res.json();

        if (data.detail) {
            setMessage(typeof data.detail === "string" ? data.detail : "Invalid input");
        } else {
            setMessage(data.message);
        }
    }

    return (
        <>
        <h2>Register</h2>
        <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <select value={userType} onChange={(e) => setUserType(e.target.value)}>
            <option value="customer">Customer</option>
            <option value="delivery_partner">Delivery Partner</option>
        </select>
        <button onClick={register}>Register</button>
        <p>{message}</p>
        </>
    );
}


export default RegisterPage