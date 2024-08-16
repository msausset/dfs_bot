import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import ItemCard from "./components/ItemCard";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./css/App.css";

const ITEMS_PER_PAGE = 50;
const TYPE_IDS = [1, 82, 9, 11, 10, 16, 17];

const App = () => {
  const [items, setItems] = useState([]);
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [gains, setGains] = useState({});
  const [itemCardsLoading, setItemCardsLoading] = useState(true); // Ajouté pour suivre le chargement des ItemCards

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
          hasMoreItems = false;
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
    fetchPrices();
  }, []);

  const handleGainCalculated = useCallback((itemId, gain) => {
    setGains((prevGains) => ({
      ...prevGains,
      [itemId]: gain,
    }));
  }, []);

  const sortItemsByGain = useCallback(() => {
    const sortedItems = [...items].sort(
      (a, b) => (gains[b.id] || 0) - (gains[a.id] || 0)
    );
    setItems(sortedItems);
  }, [items, gains]);

  useEffect(() => {
    if (items.length > 0) {
      setItemCardsLoading(false); // Tous les ItemCards sont chargés
    }
  }, [items]);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route
            path="/"
            element={
              <>
                {loading ? (
                  <p>Chargement des articles...</p>
                ) : error ? (
                  <p>{error}</p>
                ) : (
                  <>
                    {itemCardsLoading ? (
                      <p>Chargement des cartes d'articles...</p>
                    ) : (
                      <>
                        <div className="centered-button-container">
                          <button
                            className="sort-button"
                            onClick={sortItemsByGain}
                          >
                            Trier par gain
                          </button>
                        </div>
                        <div className="items-container">
                          {items.length > 0 ? (
                            items.map((item) => (
                              <ItemCard
                                key={item.id}
                                item={item}
                                prices={prices}
                                onGainCalculated={handleGainCalculated}
                              />
                            ))
                          ) : (
                            <p>Aucun item correspondant aux critères.</p>
                          )}
                        </div>
                      </>
                    )}
                  </>
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
