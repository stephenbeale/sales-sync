import { useState } from "react";
import { checkEmails } from "../utils/api";

export default function EmailChecker({ onSync }) {
  const [checking, setChecking] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleCheck = async () => {
    setChecking(true);
    setError(null);
    try {
      const data = await checkEmails();
      setResults(data);
      if (data.results.some((r) => r.auto_synced)) {
        onSync();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setChecking(false);
    }
  };

  return (
    <section className="email-checker" aria-label="Email sale detection">
      <h2>Check Vinted Emails</h2>
      <p className="hint">
        Scan Gmail for Vinted sale notifications and auto-sync
      </p>
      <button onClick={handleCheck} disabled={checking}>
        {checking ? "Checking..." : "Check for Sales"}
      </button>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {results && (
        <div className="email-results" role="status" aria-live="polite">
          <p>
            {results.sales_found === 0
              ? "No new sales found"
              : `Found ${results.sales_found} sale(s)`}
          </p>
          {results.results.map((r, i) => (
            <div key={i} className={`email-match ${r.matched ? "matched" : "unmatched"}`}>
              <p>
                <strong>{r.parsed_title}</strong>
              </p>
              {r.matched ? (
                <p className="success">
                  Matched to: {r.item_title}
                  {r.auto_synced && " — auto-synced!"}
                </p>
              ) : (
                <p className="warning">No matching item in inventory</p>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
