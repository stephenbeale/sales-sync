import { useItems } from "./hooks/useItems";
import AddItemForm from "./components/AddItemForm";
import ItemList from "./components/ItemList";
import FilterBar from "./components/FilterBar";
import EmailChecker from "./components/EmailChecker";

export default function App() {
  const {
    items,
    filter,
    setFilter,
    loading,
    error,
    addItem,
    markSold,
    removeItem,
    refresh,
  } = useItems();

  return (
    <div className="app">
      <header>
        <h1>Sales Sync</h1>
        <p className="subtitle">Keep Vinted & eBay listings in sync</p>
      </header>

      <main>
        <AddItemForm onAdd={addItem} />
        <EmailChecker onSync={refresh} />

        <section aria-label="Inventory">
          <h2>
            Inventory{" "}
            <span className="count">({items.length})</span>
          </h2>
          <FilterBar filter={filter} setFilter={setFilter} />
          <ItemList
            items={items}
            loading={loading}
            error={error}
            onSell={markSold}
            onDelete={removeItem}
          />
        </section>
      </main>
    </div>
  );
}
