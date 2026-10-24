import React, { useState } from 'react';
import { CalendarClock, CheckCircle2, Clock, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import { useKnowledge } from '../context/KnowledgeContext';
import { ReminderItem } from '../components/reminders/ReminderItem';

export const RemindersPage = () => {
  const { reminders = [] } = useKnowledge() || {};
  const [showAll, setShowAll] = useState(false);

  const safeReminders = Array.isArray(reminders) ? reminders : [];

  const pendingCount = safeReminders.filter((r) => !r?.completed).length;
  const urgentCount = safeReminders.filter((r) => r?.priority === 'urgent' && !r?.completed).length;
  const completedCount = safeReminders.filter((r) => r?.completed).length;

  // Urgent reminders (active urgent deadlines)
  const urgentReminders = safeReminders.filter((r) => r?.priority === 'urgent' && !r?.completed);

  // Remaining reminders (upcoming, normal priority, and completed)
  const otherReminders = safeReminders.filter((r) => !urgentReminders.some((u) => u.id === r?.id));

  return (
    <div className="space-y-6 pb-16 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-palette-navy dark:text-white flex items-center gap-2">
          <CalendarClock className="w-6 h-6 text-palette-slate" />
          <span>AI Detected Deadlines & Events</span>
        </h1>

        {otherReminders.length > 0 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className={`text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer ${
              showAll ? '!text-palette-clay hover:!text-palette-navy' : 'text-palette-slate hover:text-palette-navy dark:hover:text-white'
            }`}
          >
            <span>{showAll ? 'Show urgent only' : `See more (${otherReminders.length})`}</span>
            {showAll ? <ChevronUp className="w-3.5 h-3.5 text-palette-clay" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {/* Metric Stat Badges */}
      <div className="grid grid-cols-3 gap-3 sm:gap-4">
        <div className="glass-card p-4 rounded-xl">
          <div className="text-xs font-semibold text-palette-slate uppercase tracking-wider mb-1 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-palette-slate" />
            <span>Pending</span>
          </div>
          <div className="text-2xl font-bold text-palette-navy dark:text-white">{pendingCount}</div>
        </div>

        <div className="glass-card p-4 rounded-xl border border-palette-sand/60 bg-palette-sand/20">
          <div className="text-xs font-bold text-palette-clay uppercase tracking-wider mb-1 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-palette-clay" />
            <span>Urgent</span>
          </div>
          <div className="text-2xl font-extrabold text-palette-clay">{urgentCount}</div>
        </div>

        <div className="glass-card p-4 rounded-xl">
          <div className="text-xs font-semibold text-palette-slate uppercase tracking-wider mb-1 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>Completed</span>
          </div>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{completedCount}</div>
        </div>
      </div>

      {/* Reminders List */}
      <div className="space-y-4">
        {/* Urgent Reminders Section */}
        <div>
          <div className="flex items-center gap-2 mb-2.5 px-1">
            <AlertTriangle className="w-4 h-4 text-palette-clay" />
            <h2 className="text-xs font-bold text-palette-clay uppercase tracking-wider">
              Urgent Reminders ({urgentReminders.length})
            </h2>
          </div>

          {urgentReminders.length > 0 ? (
            <div className="space-y-2.5">
              {urgentReminders.map((reminder) => (
                <ReminderItem key={reminder.id} reminder={reminder} />
              ))}
            </div>
          ) : (
            <div className="glass-card rounded-xl p-5 text-center text-xs text-app-muted flex items-center justify-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>No urgent reminders pending.</span>
            </div>
          )}
        </div>

        {/* Other Reminders Section (displayed when user asks to see more) */}
        {showAll && otherReminders.length > 0 && (
          <div className="pt-2">
            <div className="flex items-center gap-2 mb-2.5 px-1">
              <Clock className="w-4 h-4 text-accent-light" />
              <h2 className="text-xs font-bold text-app-subtle uppercase tracking-wider">
                Other Reminders & Upcoming ({otherReminders.length})
              </h2>
            </div>
            <div className="space-y-2.5">
              {otherReminders.map((reminder) => (
                <ReminderItem key={reminder.id} reminder={reminder} />
              ))}
            </div>
          </div>
        )}

        {/* See More / Show Urgent Only Toggle Button */}
        {otherReminders.length > 0 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className={`w-full py-3 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer mt-2 ${
              showAll
                ? '!border-red-500/60 !text-red-500 !bg-red-500/10 hover:!bg-red-500/20 hover:!border-red-400'
                : 'border-dark-border/80 hover:border-accent/40 bg-dark-surface/40 hover:bg-dark-hover text-app-muted hover:text-white'
            }`}
          >
            <span>{showAll ? 'Show urgent reminders only' : `See more reminders (${otherReminders.length} more)`}</span>
            {showAll ? <ChevronUp className="w-4 h-4 text-red-500" /> : <ChevronDown className="w-4 h-4 text-accent-light" />}
          </button>
        )}

        {safeReminders.length === 0 && (
          <div className="glass-card rounded-2xl p-10 text-center text-xs text-app-muted">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2 opacity-50" />
            No reminders found.
          </div>
        )}
      </div>
    </div>
  );
};
