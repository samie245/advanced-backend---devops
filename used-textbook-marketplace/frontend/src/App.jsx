import {useState} from "react";
import {Routes, Route, Link} from "react-router";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import BrowsePage from "./pages/BrowsePage";
import SellPage from "./pages/SellPage";
import MyBooksPage from "./pages/MyBooksPage";

function App() {
  // the token isn't sent anywhere yet, we pass it to the pages when we protect the routes
  const [token, setToken] = useState("");

  return (
    <>
      <h1>Used Textbook Marketplace</h1>
      <nav>
        <Link to="/">Login</Link> | <Link to="/register">Register</Link> | <Link to="/listings">Browse</Link> | <Link to="/sell">Sell a book</Link> | <Link to="/my-books">My books</Link>
      </nav>
      <Routes>
        <Route path="/" element={<LoginPage setToken={setToken} />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/listings" element={<BrowsePage />} />
        <Route path="/sell" element={<SellPage />} />
        <Route path="/my-books" element={<MyBooksPage />} />
        <Route path="*" element={<h1>404 - Page Not Found</h1>} />
      </Routes>
    </>
  );
}

export default App;