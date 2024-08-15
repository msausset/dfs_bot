import React, { useState, useEffect } from "react";
import axios from "axios";
import "../css/ItemCard.css";

const ItemCard = ({ item, prices }) => {
  const [recipe, setRecipe] = useState(null); // État pour stocker les données de la recette
  const [ingredients, setIngredients] = useState([]); // État pour stocker les détails des ingrédients
  const [loading, setLoading] = useState(true); // État pour gérer le chargement
  const [error, setError] = useState(null); // État pour gérer les erreurs
  const [resourcePrices, setResourcePrices] = useState([]); // Nouvel état pour les prix des ressources

  const itemPrice = prices.find((price) => price.id === item.id);

  const formatPrice = (price) => {
    if (!price) return "";
    return parseInt(price, 10).toLocaleString("fr-FR"); // Formatage des nombres pour la France
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
    const fetchRecipe = async () => {
      try {
        const response = await axios.get(
          `https://api.dofusdb.fr/recipes?resultId=${item.id}`
        );
        const recipeData = response.data.data[0];
        setRecipe(recipeData); // Stocker les données de la recette

        // Récupérer les détails des ingrédients
        const ingredientPromises = recipeData.ingredientIds.map(
          (ingredientId) =>
            axios.get(`https://api.dofusdb.fr/items/${ingredientId}`)
        );

        const ingredientResponses = await Promise.all(ingredientPromises);
        const ingredientDetails = ingredientResponses.map(
          (response) => response.data
        );

        setIngredients(ingredientDetails); // Stocker les détails des ingrédients

        // Récupérer les prix des ressources
        const pricesResponse = await axios.get(
          "https://dfs-bot-4338ac8851d5.herokuapp.com/resources-prices"
        );
        setResourcePrices(pricesResponse.data);
      } catch (error) {
        setError("Erreur lors de la récupération des données de la recette.");
      } finally {
        setLoading(false); // Fin du chargement
      }
    };

    fetchRecipe();
  }, [item.id]);

  return (
    <div className="item-card">
      <h3>{item.name.fr}</h3>
      <p>Type: {item.type.name.fr}</p>
      <img src={item.imgset[1].url} alt={item.name.fr} />
      {itemPrice && <p>Prix: {formatPrice(itemPrice.price)} Kamas</p>}

      {loading && <p>Chargement...</p>}
      {error && <p>{error}</p>}
      {recipe && ingredients.length > 0 && (
        <div>
          <h4>Recette</h4>
          <ul>
            {recipe.ingredientIds.map((ingredientId, index) => {
              const ingredient = ingredients.find(
                (item) => item.id === ingredientId
              );
              const resourcePrice = resourcePrices.find(
                (price) => price.id === ingredientId
              );
              const quantity = recipe.quantities[index];
              const totalPrice = resourcePrice
                ? calculateTotalPrice(
                    quantity,
                    parseInt(resourcePrice.price, 10),
                    parseInt(resourcePrice.price_10, 10),
                    parseInt(resourcePrice.price_100, 10)
                  )
                : 0;

              return (
                <li key={ingredientId}>
                  {ingredient.name.fr} : {quantity} (
                  {resourcePrice
                    ? formatPrice(totalPrice) + " Kamas"
                    : "Prix non disponible"}
                  )
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ItemCard;
