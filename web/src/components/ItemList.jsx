import ItemCard from "./ItemCard";

export default function ItemList({ items, loading, error, onSell, onDelete }) {
  if (loading) return <p className="status-msg">Loading items...</p>;
  if (error) return <p className="error" role="alert">{error}</p>;
  if (items.length === 0) return <p className="status-msg">No items found.</p>;

  return (
    <ul className="item-list" aria-label="Cross-listed items">
      {items.map((item) => (
        <ItemCard
          key={item.id}
          item={item}
          onSell={onSell}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}
