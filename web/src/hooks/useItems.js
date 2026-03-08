import { useCallback, useEffect, useState } from "react";
import * as api from "../utils/api";

export function useItems() {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState("active");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getItems(filter === "all" ? null : filter);
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const addItem = async (itemData) => {
    const item = await api.createItem(itemData);
    setItems((prev) => [item, ...prev]);
    return item;
  };

  const markSold = async (id, soldOn) => {
    const result = await api.sellItem(id, soldOn);
    await fetchItems();
    return result;
  };

  const removeItem = async (id) => {
    await api.deleteItem(id);
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  const editItem = async (id, data) => {
    const updated = await api.updateItem(id, data);
    setItems((prev) => prev.map((item) => (item.id === id ? updated : item)));
    return updated;
  };

  return {
    items,
    filter,
    setFilter,
    loading,
    error,
    addItem,
    markSold,
    removeItem,
    editItem,
    refresh: fetchItems,
  };
}
