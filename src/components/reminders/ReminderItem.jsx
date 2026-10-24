import React from 'react';
import { CheckCircle2, Circle, Calendar, ExternalLink } from 'lucide-react';
import { format, isPast, isToday } from 'date-fns';
import { useKnowledge } from '../../context/KnowledgeContext';

export const ReminderItem = ({ reminder }) => {
  const { toggleReminder, items = [], openDetail } = useKnowledge() || {};

  if (!reminder) return null;

  const safeItems = Array.isArray(items) ? items : [];
  const sourceItem = safeItems.find((i) => i.id === reminder.sourceId);

  let isValidDate = false;
  let isOverdue = false;
  let isDueToday = false;
  let formattedDate = '';

  if (reminder.dueDate) {
    try {
      const parsed = new Date(reminder.dueDate);
      if (!isNaN(parsed.getTime())) {
        isValidDate = true;
        isOverdue = isPast(parsed) && !reminder.completed;
        isDueToday = isToday(parsed);
        formattedDate = format(parsed, 'MMM d, yyyy • h:mm a');
      }
    } catch {
      isValidDate = false;
    }
  }

  const getPriorityBadge = (p) => {
    switch (p) {
      case 'urgent':
        return 'bg-rose-50 text-rose-600 border border-rose-300 dark:bg-rose-950/20 dark:text-rose-400 font-bold shadow-sm';
      case 'upcoming':
        return 'bg-palette-sand/40 text-palette-clay border border-palette-clay/30 font-semibold';
      default:
        return 'bg-palette-cream text-palette-slate border border-palette-pale font-medium';
    }
  };

  return (
    <div
      className={`glass-card glass-card-hover rounded-xl p-4 flex items-center justify-between gap-4 transition-all ${
        reminder.completed ? 'opacity-50' : ''
      }`}
    >
      <div className="flex items-center gap-3.5 min-w-0">
        <button
          onClick={() => toggleReminder && toggleReminder(reminder.id)}
          className="text-app-subtle hover:text-accent-light transition-colors shrink-0 cursor-pointer"
        >
          {reminder.completed ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          ) : (
            <Circle className="w-5 h-5" />
          )}
        </button>

        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h4
              className={`text-sm font-semibold truncate ${
                reminder.completed ? 'line-through text-palette-slate/50' : 'text-palette-navy dark:text-white'
              }`}
            >
              {reminder.title || 'Untitled Reminder'}
            </h4>
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider border shrink-0 ${getPriorityBadge(
                reminder.priority
              )}`}
            >
              {reminder.priority || 'Normal'}
            </span>
          </div>

          <div className="flex items-center gap-3 text-xs text-palette-slate dark:text-app-subtle mt-1 flex-wrap">
            {isValidDate && (
              <span
                className={`flex items-center gap-1 ${
                  isOverdue ? '!text-rose-600 font-bold' : isDueToday ? 'text-palette-clay font-medium' : ''
                }`}
              >
                <Calendar className={`w-3.5 h-3.5 ${isOverdue ? 'text-rose-600' : 'text-palette-slate'}`} />
                {formattedDate}
                {isOverdue && ' (Overdue)'}
              </span>
            )}

            {sourceItem && (
              <button
                onClick={() => openDetail && openDetail(sourceItem)}
                className="flex items-center gap-1 text-palette-slate hover:text-palette-navy dark:hover:text-white hover:underline truncate cursor-pointer"
              >
                <span>From: {sourceItem.title}</span>
                <ExternalLink className="w-3 h-3 shrink-0" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
