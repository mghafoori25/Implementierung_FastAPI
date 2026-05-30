import { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../AuthContext";

type Product = {
  id: number;
  title: string;
  price: number;
  description: string;
  is_active: boolean;
  created_at: string;
};

function ProductList() {
  const [products, setProducts] = useState<Product[]>([]);
  const [message, setMessage] = useState("");

  const { logout } = useAuth();

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const response = await api.get("/products");
        setProducts(response.data);
      } catch {
        setMessage("Produkte konnten nicht geladen werden.");
      }
    };

    loadProducts();
  }, []);

  return (
    <div>
      <h1>Produktliste</h1>

      <button onClick={logout}>Logout</button>

      {message && <p>{message}</p>}

      {products.length === 0 && !message && <p>Keine Produkte gefunden.</p>}

      <ul>
        {products.map((product) => (
          <li key={product.id}>
            <strong>{product.title}</strong> – {product.price} €
            <br />
            {product.description}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ProductList;