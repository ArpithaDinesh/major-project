import React from 'react';

export const MemoraLogo = ({ size = 'md', className = '' }) => {
  const sizeMap = {
    xs: 'w-6 h-6',
    sm: 'w-8 h-8',
    md: 'w-9 h-9',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
    '2xl': 'w-24 h-24'
  };

  const containerSize = sizeMap[size] || sizeMap.md;

  return (
    <div className={`relative flex items-center justify-center shrink-0 ${containerSize} ${className}`}>
      <img
        src="/memora-emblem-transparent.png"
        alt="Memora"
        className="w-full h-full object-contain filter drop-shadow-[0_2px_8px_rgba(75,99,130,0.2)] select-none pointer-events-none"
        loading="eager"
      />
    </div>
  );
};

export const MindSyncLogo = MemoraLogo;
