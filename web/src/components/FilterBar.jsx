export default function FilterBar({ filter, setFilter }) {
  const filters = [
    { value: "active", label: "Active" },
    { value: "sold", label: "Sold" },
    { value: "all", label: "All" },
  ];

  return (
    <nav className="filter-bar" aria-label="Filter items">
      {filters.map((f) => (
        <button
          key={f.value}
          className={filter === f.value ? "active" : ""}
          onClick={() => setFilter(f.value)}
          aria-pressed={filter === f.value}
        >
          {f.label}
        </button>
      ))}
    </nav>
  );
}
