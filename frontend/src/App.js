import React, { useState, useEffect } from "react";
import axios from "axios";
import ItemCard from "./components/ItemCard";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./css/App.css";

const ITEMS_PER_PAGE = 50; // Nombre d'articles à charger par page
const TYPE_IDS = [1, 82, 9, 11, 10, 16, 17];

const App = () => {
  const [items, setItems] = useState([]);
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAllItems = async () => {
      let allItems = [];
      let currentPage = 1;
      let hasMoreItems = true;

      while (hasMoreItems) {
        try {
          const typeIdParams = TYPE_IDS.map((id) => `typeId=${id}`).join("&");
          const response = await axios.get(
            `https://api.dofusdb.fr/items?$limit=${ITEMS_PER_PAGE}&$skip=${
              (currentPage - 1) * ITEMS_PER_PAGE
            }&${typeIdParams}&level[$gt]=199`
          );

          const fetchedItems = response.data.data;
          allItems = [...allItems, ...fetchedItems];

          if (fetchedItems.length < ITEMS_PER_PAGE) {
            hasMoreItems = false;
          }

          currentPage += 1;
        } catch (error) {
          setError("Erreur lors de la récupération des articles.");
          console.error("Error fetching items:", error);
          hasMoreItems = false; // Stop the loop in case of error
        }
      }

      setItems(allItems);
      setLoading(false);
    };

    const fetchPrices = async () => {
      try {
        const response = await axios.get(
          "https://dfs-bot-4338ac8851d5.herokuapp.com/items-prices"
        );
        setPrices(response.data);
      } catch (error) {
        setError("Erreur lors de la récupération des prix.");
        console.error("Error fetching prices:", error);
      }
    };

    fetchAllItems();
    fetchPrices(); // Récupérer les prix une fois au montage du composant
  }, []);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route
            path="/"
            element={
              <>
                {loading ? (
                  <p>Chargement...</p>
                ) : error ? (
                  <p>{error}</p>
                ) : (
                  <div className="items-container">
                    {items.length > 0 ? (
                      items.map((item) => (
                        <ItemCard key={item.id} item={item} prices={prices} />
                      ))
                    ) : (
                      <p>Aucun item correspondant aux critères.</p>
                    )}
                  </div>
                )}
              </>
            }
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
