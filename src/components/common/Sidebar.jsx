import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Library, 
  Bot, 
  CalendarClock, 
  LogOut,
  Star
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useKnowledge } from '../../context/KnowledgeContext';
import { MemoraLogo } from './MemoraLogo';

export const Sidebar = () => {
  const { user, logout } = useAuth();
  const { items = [], openDetail } = useKnowledge() || {};
  const navigate = useNavigate();

  const favoriteItems = (Array.isArray(items) ? items : []).filter((item) => item?.favorite);

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/library', label: 'Library', icon: Library },
    { to: '/favorites', label: 'Favorites', icon: Star, badge: favoriteItems.length },
    { to: '/chat', label: 'AI Chatbot', icon: Bot },
    { to: '/reminders', label: 'Reminders', icon: CalendarClock },
  ];

  return (
    <aside className="hidden md:flex flex-col fixed left-0 top-0 bottom-0 z-40 w-64 bg-white/95 dark:bg-dark-card/95 backdrop-blur-2xl border-r border-palette-border dark:border-dark-border select-none">
      {/* 1. Brand Logo Header */}
      <div className="h-16 flex items-center px-5 border-b border-palette-border dark:border-dark-border shrink-0">
        <NavLink to="/" className="flex items-center gap-3 w-full group">
          <MemoraLogo size="md" className="group-hover:scale-105 transition-transform shrink-0" />
          <span className="font-bold text-lg tracking-tight text-palette-navy dark:text-white">
            MEMORA
          </span>
        </NavLink>
      </div>

      {/* 2. Middle Scrollable Area: Nav Items */}
      <nav className="flex-1 py-4 px-3.5 space-y-1.5 overflow-y-auto scrollbar-none">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isFav = item.to === '/favorites';
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `sidebar-nav-item flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all cursor-pointer group border ${
                  isActive
                    ? 'sidebar-nav-active bg-palette-navy text-white border-palette-navy shadow-sm'
                    : 'sidebar-nav-inactive bg-white dark:bg-dark-hover/40 text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white border-palette-border dark:border-dark-border/60 hover:border-palette-pale hover:bg-palette-cream/60'
                }`
              }
            >
              <div className="flex items-center gap-3 min-w-0">
                <Icon 
                  className={`w-4 h-4 transition-transform duration-200 group-hover:scale-110 shrink-0 ${
                    isFav ? 'sidebar-star-icon text-palette-clay fill-palette-clay' : 'text-palette-slate group-hover:text-palette-navy'
                  }`}
                  strokeWidth={isFav ? 0 : 2}
                />
                <span className="font-semibold text-sm truncate">{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold transition-colors ${
                  item.badge > 0
                    ? 'bg-palette-sand/40 text-palette-clay border border-palette-clay/30'
                    : 'bg-palette-cream dark:bg-dark-surface/60 text-palette-slate/70 dark:text-app-subtle border border-palette-pale dark:border-dark-border/40'
                }`}>
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* 4. User Profile Card */}
      <div className="p-3 border-t border-palette-border dark:border-dark-border shrink-0">
        <div className="sidebar-profile-card flex items-center justify-between p-2.5 rounded-2xl bg-white dark:bg-dark-card border border-palette-border dark:border-dark-border shadow-soft-card transition-all">
          <button
            onClick={() => navigate('/settings')}
            className="flex items-center gap-2.5 min-w-0 text-left cursor-pointer group"
            title="Account Settings"
          >
            <img
              src={user?.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&q=80"}
              alt="Profile"
              className="w-8 h-8 rounded-full object-cover border-2 border-palette-slate shrink-0 group-hover:scale-105 transition-transform"
            />
            <div className="min-w-0">
              <p className="sidebar-profile-name text-xs font-bold text-palette-navy dark:text-white truncate group-hover:text-palette-slate transition-colors">
                {user?.name || "Knowledge Architect"}
              </p>
              <p className="sidebar-profile-email text-[10px] font-semibold text-palette-slate dark:text-app-muted truncate">
                {user?.email || ""}
              </p>
            </div>
          </button>

          <button
            onClick={logout}
            title="Log out"
            className="sidebar-profile-logout p-1.5 text-palette-slate/60 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer shrink-0 ml-1"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
