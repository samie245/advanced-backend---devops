import {useState} from "react";
import {Link} from "react-router";


function LoginPage({setToken}) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [loggedIn, setLoggedIn] = useState(false);

    // verify login
    async function login() {
        const res = await fetch("http://localhost:8001/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username: username, password: password})
        });
        const data = await res.json();

        if (data.detail) {
            setLoggedIn(false);
            setMessage(typeof data.detail === "string" ? data.detail : "Invalid input");
        } else {
            setToken(data.access_token);
            setLoggedIn(true);
            setMessage("Logged in");
        }
    }

    return (
        <>
        <h2>Login</h2>
        <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input type= "password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button onClick={login}>Login</button>
        <p>{message}</p>
        {loggedIn && <Link to="/packages">View All Packages</Link>}
        </>
    );
}


export default LoginPage