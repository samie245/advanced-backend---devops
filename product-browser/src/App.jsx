import ProductPage from "./pages/ProductsPage";
import { Routes, Route, Link } from "react-router";
import BrowsePage from "./pages/BrowsePage";
import ProductDetailsPage from "./pages/ProductDetailsPage";


function App() {

  return (
    <>
    <nav>
    <Link to="/">All Products</Link> | <Link to="/browse">Browse</Link>
    </nav>
    <Routes>
      <Route path="/" element={<ProductPage />} />
      <Route path="/browse" element={<BrowsePage />} />
      <Route path="/products/:id" element={<ProductDetailsPage />} />
      <Route path="*" element={<h1>404 - Page Not Found</h1>} />
    </Routes>
    </>
  )
}

export default App