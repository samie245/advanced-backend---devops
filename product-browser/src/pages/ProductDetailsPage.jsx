import { useState, useEffect } from "react";
import { Link, useParams } from "react-router";

function ProductDetailsPage() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);

  useEffect(() => {
    async function loadProduct() {
      const res = await fetch(`https://dummyjson.com/products/${id}`);
      const data = await res.json();
      setProduct(data);
    }

    loadProduct();
  }, [id]);

  if (!product) return <p>Loading...</p>;

  return (
    <>
      <Link to="/">Back to Products</Link>
      <h2>{product.title}</h2>
      <p>{product.description}</p>
      <p>Price: ${product.price}</p>
      <p>Rating: {product.rating}</p>
      <p>Category: {product.category}</p>
      <p>Stock: {product.stock}</p>
      <h3>Images</h3>
      {product.images.map((image) => (
        <img key={image} src={image} width="300" />
        ))}

        <h3>Reviews</h3>
        <ul>
            {product.reviews.map((review) => (
                <li key={review.reviewerEmail}>
                    {review.reviewerName} : {review.comment}
                </li>
            ))} 
        </ul>
        
    </>
  );
}

export default ProductDetailsPage;