import {useState} from "react";
import {Routes, Route, Link} from "react-router";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import PackagesPage from "./pages/PackagesPage";


function App() {
  const [token, setToken] = useState("");

  return (
    <>
    <nav>
    <Link to="/">Login</Link> | <Link to="/register">Register</Link> | <Link to="/packages">All Packages</Link>
    </nav>
    <Routes>
      <Route path="/" element={<LoginPage setToken={setToken} />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/packages" element={<PackagesPage token={token} />} />
      <Route path="*" element={<h1>404 - Page Not Found</h1>} />
    </Routes>
    </>
  )
}

export default App