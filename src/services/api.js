import axios from 'axios';
import { INITIAL_KNOWLEDGE_ITEMS, INITIAL_REMINDERS } from './mockData';

// Load stored custom backend URL or default to /api (proxied to http://localhost:8000)
const getBaseUrl = () => {
  return localStorage.getItem('mindsync_backend_url') || localStorage.getItem('cognivault_backend_url') || import.meta.env.VITE_API_URL || '/api';
};

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token automatically to all outgoing API requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('mindsync_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Update client base URL dynamically
export const updateBackendUrl = (newUrl) => {
  apiClient.defaults.baseURL = newUrl;
  localStorage.setItem('mindsync_backend_url', newUrl);
};

export const getStoredBackendUrl = () => {
  return localStorage.getItem('mindsync_backend_url') || localStorage.getItem('cognivault_backend_url') || 'http://localhost:8000';
};

// Check if FastAPI backend is online
export const checkBackendHealth = async () => {
  try {
    const res = await apiClient.get('/health', { timeout: 2500 });
    return { online: true, data: res.data };
  } catch (err) {
    return { online: false, error: err.message };
  }
};

// Local storage backup storage keys - scoped by user ID for privacy isolation
const getCurrentUserId = () => {
  try {
    const userStr = localStorage.getItem('mindsync_user');
    if (userStr) {
      const u = JSON.parse(userStr);
      return u.id || u._id || 'guest';
    }
  } catch (e) {}
  return 'guest';
};

const getLocalItems = () => {
  const userId = getCurrentUserId();
  const key = `mindsync_items_${userId}`;
  const saved = localStorage.getItem(key);
  if (saved) {
    try { return JSON.parse(saved); } catch (e) { /* fallback */ }
  }
  return [];
};

const saveLocalItems = (items) => {
  const userId = getCurrentUserId();
  const key = `mindsync_items_${userId}`;
  localStorage.setItem(key, JSON.stringify(items));
};

const getLocalReminders = () => {
  const userId = getCurrentUserId();
  const key = `mindsync_reminders_${userId}`;
  const saved = localStorage.getItem(key);
  if (saved) {
    try { return JSON.parse(saved); } catch (e) { /* fallback */ }
  }
  return [];
};

const saveLocalReminders = (reminders) => {
  const userId = getCurrentUserId();
  const key = `mindsync_reminders_${userId}`;
  localStorage.setItem(key, JSON.stringify(reminders));
};

export const clearUserDataCache = () => {
  const userId = getCurrentUserId();
  localStorage.removeItem(`mindsync_items_${userId}`);
  localStorage.removeItem(`mindsync_reminders_${userId}`);
  localStorage.removeItem('mindsync_items_v1');
  localStorage.removeItem('mindsync_reminders_v1');
  localStorage.removeItem('cognivault_items_v1');
  localStorage.removeItem('cognivault_reminders_v1');
};

// Unified Knowledge Service with transparent fallback
export const knowledgeApi = {
  // Fetch all items
  async getItems() {
    try {
      const res = await apiClient.get('/items');
      return res.data;
    } catch {
      // Return local items fallback
      return getLocalItems();
    }
  },

  // Save new item
  async createItem(itemData) {
    try {
      const res = await apiClient.post('/items', itemData);
      return res.data;
    } catch {
      const items = getLocalItems();
      const newItem = {
        id: `item-${Date.now()}`,
        createdAt: new Date().toISOString(),
        favorite: false,
        detectedEvents: [],
        ...itemData,
      };
      const updated = [newItem, ...items];
      saveLocalItems(updated);

      // If item has detected dates, create reminders
      if (newItem.detectedEvents && newItem.detectedEvents.length > 0) {
        const reminders = getLocalReminders();
        const newReminders = newItem.detectedEvents.map((ev) => ({
          ...ev,
          sourceId: newItem.id,
          sourceTitle: newItem.title
        }));
        saveLocalReminders([...newReminders, ...reminders]);
      }

      return newItem;
    }
  },

  // Update item (correct inaccurate fields)
  async updateItem(id, updates) {
    try {
      const res = await apiClient.put(`/items/${id}`, updates);
      return res.data;
    } catch {
      const items = getLocalItems().map((item) =>
        item.id === id ? { ...item, ...updates } : item
      );
      saveLocalItems(items);
      return items.find((item) => item.id === id);
    }
  },

  // Confirm a suggested reminder from an image
  async confirmReminder(itemId, reminderData) {
    try {
      const res = await apiClient.post(`/items/${itemId}/confirm-reminder`, reminderData);
      return res.data;
    } catch {
      return this.addReminder({
        ...reminderData,
        sourceId: itemId
      });
    }
  },

  // Delete item
  async deleteItem(id) {
    try {
      await apiClient.delete(`/items/${id}`);
      return true;
    } catch {
      const items = getLocalItems().filter((item) => item.id !== id);
      saveLocalItems(items);
      const reminders = getLocalReminders().filter((r) => r.sourceId !== id);
      saveLocalReminders(reminders);
      return true;
    }
  },

  // Toggle favorite
  async toggleFavorite(id) {
    try {
      const res = await apiClient.post(`/items/${id}/favorite`);
      return res.data;
    } catch {
      const items = getLocalItems().map((item) =>
        item.id === id ? { ...item, favorite: !item.favorite } : item
      );
      saveLocalItems(items);
      return items.find((item) => item.id === id);
    }
  },

  // Fetch reminders
  async getReminders() {
    try {
      const res = await apiClient.get('/reminders');
      return res.data;
    } catch {
      return getLocalReminders();
    }
  },

  // Toggle reminder completion
  async toggleReminder(id) {
    try {
      const res = await apiClient.post(`/reminders/${id}/toggle`);
      return res.data;
    } catch {
      const reminders = getLocalReminders().map((r) =>
        r.id === id ? { ...r, completed: !r.completed } : r
      );
      saveLocalReminders(reminders);
      return reminders.find((r) => r.id === id);
    }
  },

  // Add manual reminder
  async addReminder(reminderData) {
    try {
      const res = await apiClient.post('/reminders', reminderData);
      return res.data;
    } catch {
      const reminders = getLocalReminders();
      const newReminder = {
        id: `ev-${Date.now()}`,
        completed: false,
        ...reminderData
      };
      const updated = [newReminder, ...reminders];
      saveLocalReminders(updated);
      return newReminder;
    }
  },

  // Natural Language RAG Chat
  async queryChat(prompt, history = []) {
    try {
      const res = await apiClient.post('/chat', { prompt, history });
      return res.data;
    } catch {
      // Local intelligent RAG search simulator
      await new Promise((resolve) => setTimeout(resolve, 800)); // simulated latency
      const items = getLocalItems();
      const lower = prompt.toLowerCase();

      // Find matching items by keyword/entity matching
      const matches = items.filter((item) => {
        const text = `${item.title} ${item.content} ${item.summary} ${item.tags?.join(' ')} ${item.entities?.join(' ')}`.toLowerCase();
        return lower.split(' ').some((word) => word.length > 2 && text.includes(word));
      });

      const relevant = matches.slice(0, 3);
      let reply = "";

      if (lower.includes("deadline") || lower.includes("event") || lower.includes("next")) {
        const reminders = getLocalReminders().filter(r => !r.completed);
        if (reminders.length > 0) {
          const first = reminders[0];
          reply = `Your next upcoming event is **"${first.title}"** (priority: ${first.priority}) detected from your source note: *"${first.sourceTitle}"*.`;
        } else {
          reply = "You currently have no pending upcoming deadlines or events in your knowledge base.";
        }
      } else if (relevant.length > 0) {
        reply = `Based on your stored documents and notes, here is what I found regarding **"${prompt}"**:\n\n` +
          relevant.map((item, idx) => `${idx + 1}. **${item.title}** (${item.type}): ${item.summary}`).join('\n\n') +
          `\n\nYou can click on any of the source cards below to view the complete content or extract further insights.`;
      } else {
        reply = `I searched your knowledge base for "${prompt}", but found no direct matches. Try saving a note, recording a voice memo, or pasting a relevant link into MindSync, and I will index it automatically for instant retrieval!`;
      }

      return {
        reply,
        sources: relevant.map(item => ({
          id: item.id,
          title: item.title,
          type: item.type,
          summary: item.summary,
          relevance: "94%"
        }))
      };
    }
  },

  // Process image using PaddleOCR & Image Intelligence backend
  async processImageOcr(file, category = 'General') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    // Determine target URL for backend (supports both relative /api and direct http://localhost:8000)
    const base = (getBaseUrl() || '/api').replace(/\/+$/, "");
    const primaryUrl = base.endsWith('/api') ? `${base}/process/image` : `${base}/api/process/image`;
    const secondaryUrl = base.endsWith('/api') ? `${base}/process/ocr` : `${base}/api/process/ocr`;
    const fallbackUrl = base.endsWith('/api') ? `${base}/process/upload` : `${base}/api/process/upload`;

    // Attach verified user authentication token (Requirement 2)
    const token = localStorage.getItem('mindsync_token');
    const authHeaders = {};
    if (token) {
      authHeaders['Authorization'] = `Bearer ${token}`;
    }

    // 1. Try /process/image first
    try {
      const res = await fetch(primaryUrl, {
        method: 'POST',
        headers: authHeaders,
        body: formData,
      });

      if (res.ok) {
        return await res.json();
      }

      const errText = await res.text();
      console.warn(`Endpoint /process/image returned HTTP ${res.status}:`, errText);
    } catch (fetchErr) {
      console.warn("Direct fetch /process/image failed:", fetchErr);
    }

    // 2. Try /process/ocr
    try {
      const res = await fetch(secondaryUrl, {
        method: 'POST',
        headers: authHeaders,
        body: formData,
      });

      if (res.ok) {
        return await res.json();
      }
    } catch (fetchErr2) {
      console.warn("Fetch /process/ocr failed:", fetchErr2);
    }

    // 3. Fallback to /process/upload
    try {
      const res = await fetch(fallbackUrl, {
        method: 'POST',
        headers: authHeaders,
        body: formData,
      });

      if (res.ok) {
        return await res.json();
      }
    } catch (fallbackErr) {
      console.warn("Fallback /process/upload failed:", fallbackErr);
    }

    // 4. Last fallback: apiClient with Content-Type undefined
    const apiClientRes = await apiClient.post('/process/image', formData, {
      headers: { 'Content-Type': undefined, ...authHeaders },
      timeout: 60000,
    });
    return apiClientRes.data;
  },

  async processImage(file, category = 'General') {
    return this.processImageOcr(file, category);
  },

  // Generic multi-format upload
  async processUpload(file, category = 'General') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    const base = (getBaseUrl() || '/api').replace(/\/+$/, "");
    const targetUrl = base.endsWith('/api') ? `${base}/process/upload` : `${base}/api/process/upload`;

    const token = localStorage.getItem('mindsync_token');
    const authHeaders = {};
    if (token) {
      authHeaders['Authorization'] = `Bearer ${token}`;
    }

    try {
      const res = await fetch(targetUrl, {
        method: 'POST',
        headers: authHeaders,
        body: formData,
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn("Fetch upload failed, using apiClient fallback:", e);
    }

    const res = await apiClient.post('/process/upload', formData, {
      headers: { 'Content-Type': undefined, ...authHeaders },
      timeout: 60000,
    });
    return res.data;
  }
};

// Authentication Service with JWT
export const authApi = {
  async login(email, password) {
    const res = await apiClient.post('/auth/login', { email, password });
    if (res.data?.token || res.data?.access_token) {
      const jwtToken = res.data.token || res.data.access_token;
      localStorage.setItem('mindsync_token', jwtToken);
      localStorage.setItem('mindsync_user', JSON.stringify(res.data));
    }
    return res.data;
  },

  async signup(name, email, password) {
    const res = await apiClient.post('/auth/signup', { name, email, password });
    if (res.data?.token || res.data?.access_token) {
      const jwtToken = res.data.token || res.data.access_token;
      localStorage.setItem('mindsync_token', jwtToken);
      localStorage.setItem('mindsync_user', JSON.stringify(res.data));
    }
    return res.data;
  },

  async getMe() {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },

  async updateProfile(updates) {
    const res = await apiClient.put('/auth/profile', updates);
    return res.data;
  }
};


