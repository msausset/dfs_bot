import React, { useState, useEffect } from "react";
import axios from "axios";
import "../css/ItemCard.css";

const ItemCard = ({ item, prices }) => {
  const [recipe, setRecipe] = useState(null); // État pour stocker les données de la recette
  const [ingredients, setIngredients] = useState([]); // État pour stocker les détails des ingrédients
  const [loading, setLoading] = useState(true); // État pour gérer le chargement
  const [error, setError] = useState(null); // État pour gérer les erreurs

  const itemPrice = prices.find((price) => price.id === item.id);

  const formatPrice = (price) => {
    if (!price) return "";
    return parseInt(price, 10).toLocaleString("fr-FR"); // Formatage des nombres pour la France
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
              return (
                <li key={ingredientId}>
                  {ingredient.name.fr} : {recipe.quantities[index]}
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
