import React from 'react';

export const MindSyncLogo = ({ size = 'md', className = '' }) => {
  const sizeMap = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-12 h-12',
    xl: 'w-14 h-14'
  };

  const containerSize = sizeMap[size] || sizeMap.md;

  return (
    <div className={`relative flex items-center justify-center shrink-0 ${containerSize} ${className}`}>
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <defs>
          <linearGradient id="logoSyncGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#071739"/>
            <stop offset="50%" stopColor="#4B6382"/>
            <stop offset="100%" stopColor="#A68868"/>
          </linearGradient>
        </defs>

        {/* Outer squircle frame */}
        <rect width="100" height="100" rx="26" fill="#071739" stroke="#E3C39D" strokeWidth="2.5"/>

        {/* Left Synced Neural Loop */}
        <path 
          d="M50 50 C38 32, 18 34, 18 50 C18 66, 38 68, 50 50" 
          stroke="#E3C39D" 
          strokeWidth="6.5" 
          strokeLinecap="round"
          fill="none"
        />

        {/* Right Synced Neural Loop */}
        <path 
          d="M50 50 C62 68, 82 66, 82 50 C82 34, 62 32, 50 50" 
          stroke="#A4B5C4" 
          strokeWidth="6.5" 
          strokeLinecap="round"
          fill="none"
        />

        {/* Orbit Synapse Nodes */}
        <circle cx="34" cy="38" r="4.5" fill="#E3C39D"/>
        <circle cx="66" cy="62" r="4.5" fill="#A4B5C4"/>

        {/* Central Sync Core */}
        <circle cx="50" cy="50" r="7.5" fill="#071739" stroke="#A68868" strokeWidth="3"/>
        <circle cx="50" cy="50" r="3" fill="#FFFFFF"/>
      </svg>
    </div>
  );
};
