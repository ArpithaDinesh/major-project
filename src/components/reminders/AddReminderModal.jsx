import React, { useState } from 'react';
import { X, CalendarClock, Plus } from 'lucide-react';
import { useKnowledge } from '../../context/KnowledgeContext';

export const AddReminderModal = ({ isOpen, onClose }) => {
  const { addManualReminder } = useKnowledge();
  const [title, setTitle] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState('upcoming');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    addManualReminder({
      title: title.trim(),
      dueDate: dueDate ? new Date(dueDate).toISOString() : new Date().toISOString(),
      priority,
      sourceTitle: 'Manual entry'
    });

    setTitle('');
    setDueDate('');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fadeIn">
      <div 
        className="w-full max-w-md bg-white dark:bg-dark-card border border-palette-border dark:border-dark-border rounded-2xl shadow-soft-card p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between pb-4 border-b border-dark-border mb-4">
          <div className="flex items-center gap-2">
            <CalendarClock className="w-5 h-5 text-accent-light" />
            <h3 className="text-base font-bold text-palette-navy dark:text-white">Add Reminder</h3>
          </div>
          <button onClick={onClose} className="text-palette-slate dark:text-app-subtle hover:text-palette-navy dark:hover:text-white p-1 cursor-pointer">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-palette-slate dark:text-app-muted uppercase tracking-wider mb-1.5">
              Reminder Title
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Follow up on RAG vector testing"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-white dark:bg-dark-bg border border-palette-border dark:border-dark-border focus:border-palette-navy dark:focus:border-accent rounded-xl px-3.5 py-2.5 text-sm text-palette-navy dark:text-white placeholder-palette-slate/60 dark:placeholder-app-subtle outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-palette-slate dark:text-app-muted uppercase tracking-wider mb-1.5">
                Due Date & Time
              </label>
              <input
                type="datetime-local"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="w-full bg-white dark:bg-dark-bg border border-palette-border dark:border-dark-border focus:border-palette-navy dark:focus:border-accent rounded-xl px-3 py-2 text-xs text-palette-navy dark:text-white outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-palette-slate dark:text-app-muted uppercase tracking-wider mb-1.5">
                Priority
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full bg-white dark:bg-dark-bg border border-palette-border dark:border-dark-border focus:border-palette-navy dark:focus:border-accent rounded-xl px-3 py-2 text-xs text-palette-navy dark:text-white outline-none"
              >
                <option value="urgent">Urgent</option>
                <option value="upcoming">Upcoming</option>
                <option value="normal">Normal</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2.5 pt-4 border-t border-dark-border">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-palette-navy hover:bg-palette-slate text-white text-xs font-semibold shadow-sm cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Create</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
