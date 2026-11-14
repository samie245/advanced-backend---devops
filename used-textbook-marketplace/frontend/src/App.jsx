import {useState} from "react";
import {Routes, Route, Link} from "react-router";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import BrowsePage from "./pages/BrowsePage";
import SellPage from "./pages/SellPage";
import MyBooksPage from "./pages/MyBooksPage";

// reads the role out of the token so the pages can hide what the user can't use
// this is only for the display, the backend is what actually enforces the roles
function getRole(token) {
  if (token === "") return "";
  const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
  return JSON.parse(atob(payload)).user_type;
}

function App() {
  const [token, setToken] = useState("");
  const role = getRole(token);
  const canSell = role === "seller" || role === "admin";

  return (
    <>
      <h1>Used Textbook Marketplace</h1>
      <nav>
        {token === "" ? (
          <>
            <Link to="/">Login</Link> | <Link to="/register">Register</Link>
          </>
        ) : (
          <>
            <Link to="/listings">Browse</Link> | {canSell && <><Link to="/sell">Sell a book</Link> | </>}
            <Link to="/my-books">My books</Link> | <button onClick={() => setToken("")}>Logout ({role})</button>
          </>
        )}
      </nav>
      <Routes>
        <Route path="/" element={<LoginPage setToken={setToken} />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/listings" element={<BrowsePage token={token} role={role} />} />
        <Route path="/sell" element={<SellPage token={token} role={role} />} />
        <Route path="/my-books" element={<MyBooksPage token={token} role={role} />} />
        <Route path="*" element={<h1>404 - Page Not Found</h1>} />
      </Routes>
    </>
  );
}

export default App;