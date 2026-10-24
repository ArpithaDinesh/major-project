import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Library, Star, Bot, CalendarClock } from 'lucide-react';

export const MobileNav = () => {
  const navItems = [
    { to: '/', label: 'Home', icon: LayoutDashboard },
    { to: '/library', label: 'Library', icon: Library },
    { to: '/favorites', label: 'Favorites', icon: Star },
    { to: '/chat', label: 'AI Chat', icon: Bot },
    { to: '/reminders', label: 'Reminders', icon: CalendarClock },
  ];

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 dark:bg-dark-card/95 backdrop-blur-xl border-t border-palette-border dark:border-dark-border px-2 py-1.5 shadow-soft-card">
      <div className="flex items-center justify-around">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center py-1 px-2.5 rounded-xl transition-all cursor-pointer ${
                  isActive
                    ? 'text-palette-navy dark:text-white font-semibold scale-105'
                    : 'text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] mt-0.5">{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </div>
  );
};
