import { useState } from "react";

export default function AddItemForm({ onAdd }) {
  const [title, setTitle] = useState("");
  const [ebayId, setEbayId] = useState("");
  const [vintedTitle, setVintedTitle] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    setSubmitting(true);
    setError(null);
    try {
      await onAdd({
        title: title.trim(),
        ebay_listing_id: ebayId.trim() || null,
        vinted_title: vintedTitle.trim() || null,
      });
      setTitle("");
      setEbayId("");
      setVintedTitle("");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="add-item-form" aria-label="Add cross-listed item">
      <h2>Add Item</h2>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <div className="form-field">
        <label htmlFor="item-title">Item Title</label>
        <input
          id="item-title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Nike Air Max 90 Size 10"
          required
        />
      </div>
      <div className="form-field">
        <label htmlFor="ebay-id">eBay Listing ID</label>
        <input
          id="ebay-id"
          type="text"
          value={ebayId}
          onChange={(e) => setEbayId(e.target.value)}
          placeholder="e.g. 123456789012"
        />
      </div>
      <div className="form-field">
        <label htmlFor="vinted-title">
          Vinted Title <span className="hint">(if different)</span>
        </label>
        <input
          id="vinted-title"
          type="text"
          value={vintedTitle}
          onChange={(e) => setVintedTitle(e.target.value)}
          placeholder="Leave blank if same as title"
        />
      </div>
      <button type="submit" disabled={submitting || !title.trim()}>
        {submitting ? "Adding..." : "Add Item"}
      </button>
    </form>
  );
}
