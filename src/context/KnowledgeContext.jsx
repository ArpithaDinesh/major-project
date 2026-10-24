import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { knowledgeApi, checkBackendHealth } from '../services/api';
import { useToast } from './ToastContext';
import { useAuth } from './AuthContext';

const KnowledgeContext = createContext(null);

export const KnowledgeProvider = ({ children }) => {
  const { addToast } = useToast();
  const { user, token } = useAuth();
  const [items, setItems] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState('checking'); // 'online' | 'offline' | 'checking'

  // Filter & Search states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedType, setSelectedType] = useState('All');
  const [selectedSort, setSelectedSort] = useState('newest');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'list'

  // Modal states
  const [isCaptureOpen, setIsCaptureOpen] = useState(false);
  const [captureInitialTab, setCaptureInitialTab] = useState('note');
  const [selectedItemDetail, setSelectedItemDetail] = useState(null);

  // Initial load
  const loadData = async () => {
    setLoading(true);
    try {
      const [fetchedItems, fetchedReminders] = await Promise.all([
        knowledgeApi.getItems(),
        knowledgeApi.getReminders(),
      ]);
      setItems(fetchedItems);
      setReminders(fetchedReminders);
    } catch {
      addToast("Failed to load knowledge items", "error");
    } finally {
      setLoading(false);
    }
  };

  const checkHealth = async () => {
    const health = await checkBackendHealth();
    setBackendStatus(health.online ? 'online' : 'offline');
  };

  useEffect(() => {
    if (token && user?.id) {
      loadData();
    } else {
      setItems([]);
      setReminders([]);
      setLoading(false);
    }
    checkHealth();
  }, [user?.id, token]);

  // Capture modal helpers
  const openCapture = (tab = 'note') => {
    setCaptureInitialTab(tab);
    setIsCaptureOpen(true);
  };

  const closeCapture = () => {
    setIsCaptureOpen(false);
  };

  // Item details modal helpers
  const openDetail = (item) => {
    setSelectedItemDetail(item);
  };

  const closeDetail = () => {
    setSelectedItemDetail(null);
  };

  // CRUD actions
  const addItem = async (newItemData) => {
    try {
      const created = await knowledgeApi.createItem(newItemData);
      setItems((prev) => [created, ...prev]);

      // If new item generated detected events, refresh reminders
      if (created.detectedEvents && created.detectedEvents.length > 0) {
        const updatedReminders = await knowledgeApi.getReminders();
        setReminders(updatedReminders);
      }

      addToast(`"${created.title}" successfully indexed by AI!`, 'success');
      return created;
    } catch (err) {
      addToast("Failed to save item: " + err.message, "error");
      throw err;
    }
  };

  const deleteItem = async (id) => {
    try {
      await knowledgeApi.deleteItem(id);
      setItems((prev) => prev.filter((it) => it.id !== id));
      setReminders((prev) => prev.filter((r) => r.sourceId !== id));
      if (selectedItemDetail?.id === id) {
        closeDetail();
      }
      addToast("Item removed from knowledge base", "info");
    } catch (err) {
      addToast("Failed to delete item", "error");
    }
  };

  const toggleFavorite = async (id) => {
    try {
      const updated = await knowledgeApi.toggleFavorite(id);
      setItems((prev) => prev.map((it) => (it.id === id ? updated : it)));
      if (selectedItemDetail?.id === id) {
        setSelectedItemDetail(updated);
      }
      addToast(
        updated.favorite ? "Added to favorites" : "Removed from favorites",
        "info"
      );
    } catch {
      addToast("Failed to toggle favorite", "error");
    }
  };

  const toggleReminder = async (id) => {
    try {
      const updated = await knowledgeApi.toggleReminder(id);
      setReminders((prev) => prev.map((r) => (r.id === id ? updated : r)));
      addToast(
        updated.completed ? "Reminder completed!" : "Reminder marked active",
        "info"
      );
    } catch {
      addToast("Failed to update reminder", "error");
    }
  };

  const addManualReminder = async (data) => {
    try {
      const created = await knowledgeApi.addReminder(data);
      setReminders((prev) => [created, ...prev]);
      addToast("New reminder created", "success");
      return created;
    } catch {
      addToast("Failed to create reminder", "error");
    }
  };

  const updateItem = async (id, updates) => {
    try {
      const updated = await knowledgeApi.updateItem(id, updates);
      setItems((prev) => prev.map((it) => (it.id === id ? updated : it)));
      if (selectedItemDetail?.id === id) {
        setSelectedItemDetail(updated);
      }
      addToast("Item updated successfully", "success");
      return updated;
    } catch (err) {
      addToast("Failed to update item: " + err.message, "error");
      throw err;
    }
  };

  const confirmReminder = async (itemId, reminderData) => {
    try {
      const rem = await knowledgeApi.confirmReminder(itemId, reminderData);
      setReminders((prev) => [rem, ...prev]);
      // Update item in state so suggestedReminders shows confirmed
      setItems((prev) =>
        prev.map((it) => {
          if (it.id === itemId) {
            const sugs = (it.suggestedReminders || []).map((s) =>
              s.title === reminderData.title || s.dueDate === reminderData.dueDate
                ? { ...s, confirmed: true }
                : s
            );
            const updated = { ...it, suggestedReminders: sugs };
            if (selectedItemDetail?.id === itemId) {
              setSelectedItemDetail(updated);
            }
            return updated;
          }
          return it;
        })
      );
      addToast(`Reminder added: "${reminderData.title}"`, "success");
      return rem;
    } catch (err) {
      addToast("Failed to create reminder: " + err.message, "error");
      throw err;
    }
  };

  // Dynamic categories and tags extracted from current items
  const categories = useMemo(() => {
    const set = new Set(['All']);
    items.forEach((it) => {
      if (it.category) set.add(it.category);
    });
    return Array.from(set);
  }, [items]);

  const allTags = useMemo(() => {
    const set = new Set();
    items.forEach((it) => {
      if (it.tags && Array.isArray(it.tags)) {
        it.tags.forEach((tag) => set.add(tag));
      }
    });
    return Array.from(set);
  }, [items]);

  // Filtered & Sorted items computation
  const filteredItems = useMemo(() => {
    return items
      .filter((item) => {
        // Search filter
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const titleMatch = item.title?.toLowerCase().includes(q);
          const summaryMatch = item.summary?.toLowerCase().includes(q);
          const contentMatch = item.content?.toLowerCase().includes(q);
          const tagMatch = item.tags?.some((t) => t.toLowerCase().includes(q));
          const entityMatch = item.entities?.some((e) => e.toLowerCase().includes(q));
          if (!titleMatch && !summaryMatch && !contentMatch && !tagMatch && !entityMatch) {
            return false;
          }
        }
        // Type filter
        if (selectedType !== 'All' && item.type !== selectedType) {
          return false;
        }
        // Category filter
        if (selectedCategory !== 'All' && item.category !== selectedCategory) {
          return false;
        }
        return true;
      })
      .sort((a, b) => {
        if (selectedSort === 'newest') {
          return new Date(b.createdAt) - new Date(a.createdAt);
        }
        if (selectedSort === 'oldest') {
          return new Date(a.createdAt) - new Date(b.createdAt);
        }
        if (selectedSort === 'title') {
          return a.title.localeCompare(b.title);
        }
        return 0;
      });
  }, [items, searchQuery, selectedCategory, selectedType, selectedSort]);

  return (
    <KnowledgeContext.Provider
      value={{
        items,
        filteredItems,
        reminders,
        loading,
        backendStatus,
        checkHealth,
        categories,
        allTags,
        // Filters
        searchQuery,
        setSearchQuery,
        selectedCategory,
        setSelectedCategory,
        selectedType,
        setSelectedType,
        selectedSort,
        setSelectedSort,
        viewMode,
        setViewMode,
        // Modal & actions
        isCaptureOpen,
        captureInitialTab,
        openCapture,
        closeCapture,
        selectedItemDetail,
        openDetail,
        closeDetail,
        addItem,
        updateItem,
        confirmReminder,
        deleteItem,
        toggleFavorite,
        toggleReminder,
        addManualReminder,
        loadData
      }}
    >
      {children}
    </KnowledgeContext.Provider>
  );
};

export const useKnowledge = () => {
  const context = useContext(KnowledgeContext);
  if (!context) throw new Error("useKnowledge must be used within KnowledgeProvider");
  return context;
};
