import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Search, Sun, Moon } from 'lucide-react';
import { useKnowledge } from '../../context/KnowledgeContext';
import { useAuth } from '../../context/AuthContext';
import { MemoraLogo } from './MemoraLogo';

export const Header = () => {
  const { searchQuery, setSearchQuery } = useKnowledge() || {};
  const { user } = useAuth() || {};
  const navigate = useNavigate();
  const location = useLocation();

  // Light / Dark Theme toggle state
  const [isDark, setIsDark] = useState(() => {
    return !document.documentElement.classList.contains('light');
  });

  // Ensure theme preference is loaded and applied on mount
  useEffect(() => {
    const saved = localStorage.getItem('memora_theme') || localStorage.getItem('mindsync_theme');
    if (saved === 'light') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      setIsDark(false);
    } else if (saved === 'dark') {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
      setIsDark(true);
    }
  }, []);

  const toggleTheme = () => {
    if (document.documentElement.classList.contains('light')) {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
      localStorage.setItem('memora_theme', 'dark');
      localStorage.setItem('mindsync_theme', 'dark');
      setIsDark(true);
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      localStorage.setItem('memora_theme', 'light');
      localStorage.setItem('mindsync_theme', 'light');
      setIsDark(false);
    }
  };

  const handleSearchChange = (e) => {
    if (setSearchQuery) {
      setSearchQuery(e.target.value);
    }
    if (location.pathname !== '/library' && location.pathname !== '/favorites') {
      navigate('/library');
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-palette-cream/90 backdrop-blur-xl border-b border-palette-border px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
      {/* Mobile Brand Title (visible only on small screens when sidebar is hidden) */}
      <div className="flex items-center gap-2.5 md:hidden">
        <MemoraLogo size="sm" />
        <span className="font-bold text-base tracking-tight text-palette-navy dark:text-white">Memora</span>
      </div>

      {/* Global Knowledge Search Bar */}
      <div className="flex-1 max-w-xl relative">
        <Search className="w-4 h-4 text-palette-slate absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={searchQuery || ''}
          onChange={handleSearchChange}
          placeholder="Search notes, audio memos, documents, slides, links..."
          className="header-search-input w-full bg-white border border-palette-pale focus:border-palette-slate rounded-xl pl-10 pr-12 py-2 text-xs sm:text-sm font-medium placeholder-[#8B9BAE] transition-all outline-none"
        />
        <div className="hidden sm:flex items-center absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-palette-slate px-1.5 py-0.5 rounded border border-palette-pale bg-palette-cream font-mono">
          ⌘K
        </div>
      </div>

      {/* Right Action Controls: Light/Dark Theme Switcher aligned with Search Area & Profile */}
      <div className="flex items-center gap-2.5 shrink-0">
        <button
          onClick={toggleTheme}
          aria-label="Toggle light/dark theme"
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer group border ${
            isDark
              ? 'bg-[#0E244B] border-[#244983] hover:border-[#4B6382] text-white'
              : 'bg-white border-[#CDD5DB] hover:border-[#4B6382] text-palette-navy shadow-sm'
          }`}
          title="Toggle light or dark theme"
        >
          {isDark ? (
            <>
              <Sun className="w-3.5 h-3.5 text-[#E3C39D] group-hover:rotate-45 transition-transform" />
              <span className="hidden sm:inline text-white">Light Mode</span>
            </>
          ) : (
            <>
              <Moon className="w-3.5 h-3.5 text-palette-slate group-hover:-rotate-12 transition-transform" />
              <span className="hidden sm:inline text-palette-navy font-semibold">Dark Mode</span>
            </>
          )}
        </button>

        {/* User Profile Avatar */}
        <button
          onClick={() => navigate('/settings')}
          className="flex items-center gap-2 p-0.5 rounded-full hover:ring-2 hover:ring-accent/50 transition-all cursor-pointer"
          title="Account & Settings"
        >
          <img
            src={user?.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&q=80"}
            alt="Profile"
            className="w-8 h-8 rounded-full object-cover border border-palette-slate/40"
          />
        </button>
      </div>
    </header>
  );
};
