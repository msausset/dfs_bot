import React, { useState, useEffect } from "react";
import axios from "axios";
import "../css/ItemCard.css";

const ItemCard = ({ item, prices, onGainCalculated }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalIngredientsPrice, setTotalIngredientsPrice] = useState(0);

  const itemPrice = prices.find((price) => price.id === item.id);

  const formatPrice = (price) => {
    if (!price) return "";
    return parseInt(price, 10).toLocaleString("fr-FR");
  };

  const calculateTotalPrice = (quantity, price, price10, price100) => {
    let totalPrice = 0;
    if (quantity >= 100) {
      const hundreds = Math.floor(quantity / 100);
      quantity %= 100;
      totalPrice += hundreds * price100;
    }
    if (quantity >= 10) {
      const tens = Math.floor(quantity / 10);
      quantity %= 10;
      totalPrice += tens * price10;
    }
    totalPrice += quantity * price;
    return totalPrice;
  };

  useEffect(() => {
    const fetchRecipeAndPrices = async () => {
      try {
        const response = await axios.get(
          `https://api.dofusdb.fr/recipes?resultId=${item.id}`
        );
        const recipeData = response.data.data[0];

        const pricesResponse = await axios.get(
          "https://dfs-bot-4338ac8851d5.herokuapp.com/resources-prices"
        );

        let totalPrice = 0;
        recipeData.ingredientIds.forEach((ingredientId, index) => {
          const quantity = recipeData.quantities[index];
          const resourcePrice = pricesResponse.data.find(
            (price) => price.id === ingredientId
          );

          if (resourcePrice) {
            const price = parseInt(resourcePrice.price, 10);
            const price10 = parseInt(resourcePrice.price_10, 10);
            const price100 = parseInt(resourcePrice.price_100, 10);
            totalPrice += calculateTotalPrice(
              quantity,
              price,
              price10,
              price100
            );
          }
        });

        setTotalIngredientsPrice(totalPrice);
      } catch (error) {
        setError("Erreur lors de la récupération des données de la recette.");
      } finally {
        setLoading(false);
      }
    };

    fetchRecipeAndPrices();
  }, [item.id]);

  const calculateProfit = () => {
    if (!itemPrice || totalIngredientsPrice <= 0) return null;
    return itemPrice.price - totalIngredientsPrice;
  };

  const profit = calculateProfit();

  useEffect(() => {
    if (profit !== null) {
      onGainCalculated(item.id, profit);
    }
  }, [profit, onGainCalculated, item.id]);

  return (
    <div
      className={`item-card ${
        profit !== null ? (profit > 0 ? "beneficial" : "not-beneficial") : ""
      }`}
    >
      <h3 className="h3class">{item.name.fr}</h3>
      <img src={item.imgset[1].url} alt={item.name.fr} />
      {loading && <p>Chargement...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && profit !== null && (
        <div>
          <p>
            {profit > 0 ? "+" : ""}
            {formatPrice(profit)} K
          </p>
        </div>
      )}
    </div>
  );
};

export default ItemCard;
