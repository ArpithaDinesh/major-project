import React from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Library, 
  Bot, 
  CalendarClock, 
  Settings, 
  Search, 
  Download, 
  Sparkles, 
  Server, 
  LogOut,
  Layers
} from 'lucide-react';
import { useKnowledge } from '../../context/KnowledgeContext';
import { useAuth } from '../../context/AuthContext';
import { usePWAInstall } from '../../hooks/usePWAInstall';
import { MindSyncLogo } from './MindSyncLogo';

export const TopNav = () => {
  const { searchQuery, setSearchQuery, backendStatus } = useKnowledge();
  const { user, logout } = useAuth();
  const { isInstallable, promptInstall } = usePWAInstall();
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/library', label: 'Library', icon: Library },
    { to: '/chat', label: 'AI Chat', icon: Bot },
    { to: '/reminders', label: 'Reminders', icon: CalendarClock },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    if (location.pathname !== '/library') {
      navigate('/library');
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-white/85 dark:bg-dark-bg/85 backdrop-blur-xl border-b border-palette-border dark:border-dark-border/80 shadow-soft-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* 1. Left: MindSync Brand */}
          <NavLink to="/" className="flex items-center gap-3 group shrink-0">
            <MindSyncLogo size="md" className="group-hover:scale-105 transition-transform" />
            <span className="font-bold text-lg tracking-tight theme-gradient-text">
              MindSync
            </span>
          </NavLink>

          {/* 2. Center: Horizontal Navigation Links (Arranged Horizontally) */}
          <nav className="flex items-center gap-1 sm:gap-1.5 overflow-x-auto py-1 scrollbar-none">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 sm:px-3.5 py-1.5 sm:py-2 rounded-xl text-xs sm:text-sm font-medium transition-all whitespace-nowrap cursor-pointer group ${
                      isActive
                        ? 'bg-palette-navy text-white border border-palette-navy shadow-sm'
                        : 'text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white hover:bg-palette-cream/70 dark:hover:bg-dark-hover/70'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 transition-colors group-hover:text-palette-navy dark:group-hover:text-accent-light" />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="hidden md:inline-block text-[9px] uppercase tracking-wider font-semibold px-1.5 py-0.2 rounded-full bg-palette-sand/40 text-palette-clay border border-palette-clay/30">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>

          {/* 3. Right: Search & User Controls */}
          <div className="flex items-center gap-2.5 shrink-0">
            {/* Search Input (visible on medium+ screens) */}
            <div className="hidden lg:flex items-center relative w-48 xl:w-60">
              <Search className="w-3.5 h-3.5 text-palette-slate/70 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Search vault..."
                className="w-full bg-white dark:bg-dark-surface/90 border border-palette-pale dark:border-dark-border/80 focus:border-palette-navy dark:focus:border-accent/60 rounded-xl pl-9 pr-8 py-1.5 text-xs text-palette-navy dark:text-white placeholder-app-subtle outline-none"
              />
              <div className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[9px] text-palette-slate/60 px-1 py-0.2 rounded border border-palette-pale dark:border-dark-border bg-palette-cream dark:bg-dark-bg font-mono">
                ⌘K
              </div>
            </div>

            {/* Backend Status indicator */}
            <div 
              title={backendStatus === 'online' ? 'FastAPI Connected' : 'Local AI Sync (Offline Ready)'}
              className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-palette-cream/70 dark:bg-dark-surface/80 border border-palette-border dark:border-dark-border text-[11px] text-palette-slate dark:text-app-muted"
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  backendStatus === 'online'
                    ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]'
                    : 'bg-palette-clay shadow-[0_0_8px_#A68868]'
                }`}
              />
              <span className="hidden xl:inline text-[10px]">
                {backendStatus === 'online' ? 'FastAPI' : 'Local AI'}
              </span>
            </div>

            {/* Install button if PWA installable */}
            {isInstallable && (
              <button
                onClick={promptInstall}
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-palette-sand/40 text-palette-clay border border-palette-clay/40 hover:bg-palette-sand/60 transition-all cursor-pointer shadow-sm"
              >
                <Download className="w-3 h-3" />
                <span>Install</span>
              </button>
            )}

            {/* Profile Avatar */}
            <button
              onClick={() => navigate('/settings')}
              className="flex items-center gap-2 p-0.5 rounded-full hover:ring-2 hover:ring-accent/50 transition-all cursor-pointer"
              title="Settings & Profile"
            >
              <img
                src={user?.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&q=80"}
                alt="Profile"
                className="w-8 h-8 rounded-full object-cover border border-palette-slate/40"
              />
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};
