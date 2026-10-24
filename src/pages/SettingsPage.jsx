import React, { useState, useEffect } from 'react';
import { User, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useKnowledge } from '../context/KnowledgeContext';
import { useToast } from '../context/ToastContext';

export const SettingsPage = () => {
  const { user, updateProfile, logout } = useAuth() || {};
  const { items = [] } = useKnowledge() || {};
  const { addToast } = useToast() || {};

  // Profile fields
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');

  useEffect(() => {
    setName(user?.name || '');
    setEmail(user?.email || '');
  }, [user]);

  const handleSaveProfile = (e) => {
    e.preventDefault();
    updateProfile({ name, email });
    addToast("Profile preferences updated", "success");
  };

  return (
    <div className="space-y-8 pb-16 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-palette-navy dark:text-white">System Settings & Profile</h1>
        <p className="text-sm text-palette-slate dark:text-app-muted mt-1">
          Manage your account profile and display preferences.
        </p>
      </div>

      {/* Profile Section */}
      <div className="glass-card rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-palette-navy dark:text-white flex items-center gap-2">
            <User className="w-5 h-5 text-palette-slate" />
            <span>User Profile</span>
          </h2>
          <button
            onClick={logout}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-rose-50 hover:bg-rose-100 dark:bg-rose-500/10 dark:hover:bg-rose-500/20 border border-rose-200 dark:border-rose-500/30 text-rose-600 dark:text-rose-300 text-xs font-semibold cursor-pointer transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>

        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div className="flex items-center gap-4 pb-2">
            <img
              src={user?.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"}
              alt="Avatar"
              className="w-16 h-16 rounded-full object-cover border-2 border-palette-slate/40"
            />
            <div>
              <p className="text-sm font-semibold text-palette-navy dark:text-white">{user?.name}</p>
              <p className="text-xs text-palette-slate/70 dark:text-app-subtle">{user?.plan}</p>
              <p className="text-[11px] text-palette-clay mt-0.5">
                Storage: {items?.length || 0} items (~14.2 MB) of 5 GB
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-palette-slate dark:text-app-muted uppercase tracking-wider mb-1.5">
                Display Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-white dark:bg-dark-bg border border-palette-pale dark:border-dark-border focus:border-palette-navy dark:focus:border-palette-sand rounded-xl px-3.5 py-2.5 text-sm text-palette-navy dark:text-white outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-palette-slate dark:text-app-muted uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-white dark:bg-dark-bg border border-palette-pale dark:border-dark-border focus:border-palette-navy dark:focus:border-palette-sand rounded-xl px-3.5 py-2.5 text-sm text-palette-navy dark:text-white outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-palette-navy hover:bg-palette-slate text-white text-xs font-semibold cursor-pointer transition-colors shadow-sm"
          >
            Save Profile Changes
          </button>
        </form>
      </div>
    </div>
  );
};
