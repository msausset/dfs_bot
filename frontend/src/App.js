import React, { useState, useEffect } from "react";
import axios from "axios";
import ItemCard from "./components/ItemCard";
import Pagination from "./components/navigation/Pagination";
import RecipeCard from "./components/RecipeCard";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./css/App.css";

const ITEMS_PER_PAGE = 50;
const TYPE_IDS = [1, 82, 9, 11, 10, 16, 17];

const App = () => {
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [page, setPage] = useState(1);
  const [prices, setPrices] = useState([]); // Nouvel état pour les prix

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const typeIdParams = TYPE_IDS.map((id) => `typeId=${id}`).join("&");
        const response = await axios.get(
          `https://api.dofusdb.fr/items?$limit=${ITEMS_PER_PAGE}&$skip=${
            (page - 1) * ITEMS_PER_PAGE
          }&${typeIdParams}&level[$gt]=199`
        );

        setItems(response.data.data);
        setTotalItems(response.data.total);
      } catch (error) {
        console.error("Error fetching items:", error);
      }
    };

    const fetchPrices = async () => {
      try {
        const response = await axios.get("http://localhost:5000/prices");
        setPrices(response.data);
      } catch (error) {
        console.error("Error fetching prices:", error);
      }
    };

    fetchItems();
    fetchPrices(); // Récupérer les prix une fois au montage du composant
  }, [page]);

  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

  return (
    <Router>
      <div className="App">
        <h1>Items DofusDB</h1>
        <Routes>
          <Route
            path="/"
            element={
              <>
                {items.length > 0 ? (
                  items.map((item) => (
                    <ItemCard key={item.id} item={item} prices={prices} />
                  ))
                ) : (
                  <p>Aucun item correspondant aux critères.</p>
                )}
                <Pagination
                  page={page}
                  totalPages={totalPages}
                  onPageChange={setPage}
                />
              </>
            }
          />
          <Route path="/recipe/:id" element={<RecipeCard />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
