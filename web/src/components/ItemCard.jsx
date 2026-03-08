import { useState } from "react";

export default function ItemCard({ item, onSell, onDelete }) {
  const [selling, setSelling] = useState(false);
  const [result, setResult] = useState(null);

  const handleSell = async (soldOn) => {
    setSelling(true);
    try {
      const res = await onSell(item.id, soldOn);
      setResult(res);
    } catch (err) {
      setResult({ error: err.message });
    } finally {
      setSelling(false);
    }
  };

  const isActive = item.status === "active";

  return (
    <li className={`item-card ${item.status}`}>
      <div className="item-header">
        <h3>{item.title}</h3>
        <span className={`status-badge ${item.status}`}>{item.status}</span>
      </div>

      <div className="item-details">
        {item.ebay_listing_id && (
          <p>
            <span className="label">eBay ID:</span> {item.ebay_listing_id}
          </p>
        )}
        {item.vinted_title && item.vinted_title !== item.title && (
          <p>
            <span className="label">Vinted title:</span> {item.vinted_title}
          </p>
        )}
        {item.sold_on && (
          <p>
            <span className="label">Sold on:</span> {item.sold_on}
          </p>
        )}
        {item.sold_at && (
          <p>
            <span className="label">Sold at:</span>{" "}
            {new Date(item.sold_at).toLocaleDateString()}
          </p>
        )}
      </div>

      {isActive && (
        <div className="item-actions">
          <button
            onClick={() => handleSell("vinted")}
            disabled={selling}
            className="btn-vinted"
            aria-label={`Mark ${item.title} as sold on Vinted`}
          >
            {selling ? "Syncing..." : "Sold on Vinted"}
          </button>
          <button
            onClick={() => handleSell("ebay")}
            disabled={selling}
            className="btn-ebay"
            aria-label={`Mark ${item.title} as sold on eBay`}
          >
            {selling ? "Syncing..." : "Sold on eBay"}
          </button>
          <button
            onClick={() => onDelete(item.id)}
            className="btn-delete"
            aria-label={`Remove ${item.title}`}
          >
            Remove
          </button>
        </div>
      )}

      {result && (
        <div
          className={`sync-result ${result.error ? "error" : "success"}`}
          role="status"
          aria-live="polite"
        >
          {result.error ? (
            <p>Error: {result.error}</p>
          ) : (
            <>
              <p>Marked as sold on {result.sold_on}</p>
              {result.ebay_ended === true && <p>eBay listing ended</p>}
              {result.ebay_ended === false && (
                <p className="warning">
                  Failed to end eBay listing: {result.ebay_error}
                </p>
              )}
              {result.sold_on === "ebay" && (
                <p className="reminder">
                  Remember to mark as sold/remove on Vinted manually
                </p>
              )}
            </>
          )}
        </div>
      )}
    </li>
  );
}
