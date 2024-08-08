import React from "react";

const Pagination = ({ page, totalPages, onPageChange }) => {
  return (
    <div className="pagination">
      {page > 1 && (
        <button onClick={() => onPageChange(page - 1)}>Précédent</button>
      )}
      {[...Array(totalPages).keys()].map((p) => (
        <button
          key={p + 1}
          onClick={() => onPageChange(p + 1)}
          style={{ fontWeight: p + 1 === page ? "bold" : "normal" }}
        >
          {p + 1}
        </button>
      ))}
      {page < totalPages && (
        <button onClick={() => onPageChange(page + 1)}>Suivant</button>
      )}
    </div>
  );
};

export default Pagination;
