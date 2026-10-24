import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowRight,
  CalendarClock,
  Clock
} from 'lucide-react';
import { useKnowledge } from '../context/KnowledgeContext';
import { useAuth } from '../context/AuthContext';
import { ContentCard } from '../components/library/ContentCard';
import { ReminderItem } from '../components/reminders/ReminderItem';

export const DashboardPage = () => {
  const { items = [], reminders = [] } = useKnowledge() || {};
  const { user } = useAuth() || {};
  const navigate = useNavigate();

  const safeItems = Array.isArray(items) ? items : [];
  const safeReminders = Array.isArray(reminders) ? reminders : [];

  const pendingReminders = safeReminders.filter((r) => !r?.completed);

  // STRICTLY RECENTLY ADDED ITEMS (Top 3 newest items)
  const recentlyAddedItems = [...safeItems]
    .sort((a, b) => new Date(b?.createdAt || 0) - new Date(a?.createdAt || 0))
    .slice(0, 3);

  // Top pending deadlines
  const upcomingDeadlines = pendingReminders.slice(0, 3);

  return (
    <div className="space-y-7 max-w-7xl mx-auto">
      {/* 1. Header Bar: Clean Greeting */}
      <div className="pt-1">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-palette-navy dark:text-white">
          Welcome back, {user?.name?.split(' ')[0] || 'Architect'}
        </h1>
      </div>

      {/* 2. RECENTLY ADDED ITEMS ONLY */}
      <section className="space-y-3.5">
        <div className="flex items-center justify-between border-b border-palette-border dark:border-dark-border/60 pb-2.5">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-palette-slate" />
            <h2 className="text-sm font-bold text-palette-navy dark:text-white tracking-wide">
              Recently Added Items
            </h2>
          </div>

          <button
            onClick={() => navigate('/library')}
            className="dashboard-browse-btn px-3.5 py-1.5 rounded-xl bg-palette-navy hover:bg-palette-slate text-white font-semibold text-xs flex items-center gap-1.5 transition-all cursor-pointer shadow-sm group"
          >
            <span className="font-semibold text-white">
              Browse Library ({safeItems.length})
            </span>
            <ArrowRight className="w-3.5 h-3.5 text-palette-sand group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>

        {recentlyAddedItems.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentlyAddedItems.map((item) => (
              <ContentCard key={item.id} item={item} showTags={false} showCategory={false} />
            ))}
          </div>
        ) : (
          <div className="glass-card rounded-2xl p-8 text-center text-xs text-palette-slate">
            <Clock className="w-8 h-8 text-palette-slate/40 mx-auto mb-2 opacity-50" />
            <p className="text-palette-navy dark:text-white font-semibold mb-1">No recently added items</p>
            <p className="text-[11px] text-palette-slate max-w-sm mx-auto">
              Use the floating + button in the bottom right corner to capture text, voice memos, images, PDFs, PPTs, or links.
            </p>
          </div>
        )}
      </section>

      {/* 3. Upcoming Deadlines & Detected Events Section */}
      {upcomingDeadlines.length > 0 && (
        <section className="space-y-3 pt-2">
          <div className="flex items-center justify-between border-b border-palette-border dark:border-dark-border/60 pb-2.5">
            <div className="flex items-center gap-2">
              <CalendarClock className="w-4 h-4 text-palette-clay" />
              <h2 className="text-sm font-bold text-palette-navy dark:text-white tracking-wide">
                Upcoming Deadlines & Actions
              </h2>
            </div>

            <button
              onClick={() => navigate('/reminders')}
              className="text-xs font-semibold text-palette-slate hover:text-palette-navy dark:hover:text-white flex items-center gap-1 transition-colors cursor-pointer"
            >
              <span>Manage all</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-2.5 max-w-3xl">
            {upcomingDeadlines.map((reminder) => (
              <ReminderItem key={reminder.id} reminder={reminder} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
