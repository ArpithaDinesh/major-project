import React from 'react';

/**
 * Standard Memora Vector Logo Mark
 * Concept: Two 3D glassmorphic knowledge cards enclosed by a luminous golden orbit
 * with a celestial satellite orb and a radiant 4-pointed intelligence star.
 */
export const MemoraLogo = ({ size = 'md', className = '', variant = 'emblem' }) => {
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
      <svg
        viewBox="0 0 256 256"
        className="w-full h-full object-contain filter drop-shadow-[0_4px_14px_rgba(75,99,130,0.25)] select-none pointer-events-none transition-transform duration-300"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Back Card Gradient: Deep Navy & Slate */}
          <linearGradient id="memora-card-back" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4B6382"/>
            <stop offset="45%" stopColor="#122D5C"/>
            <stop offset="100%" stopColor="#071739"/>
          </linearGradient>

          {/* Front Card Gradient: Frosted Glass with Warm Sandstone Tint */}
          <linearGradient id="memora-card-front" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.95"/>
            <stop offset="30%" stopColor="#F7F5EE" stopOpacity="0.90"/>
            <stop offset="70%" stopColor="#E3C39D" stopOpacity="0.80"/>
            <stop offset="100%" stopColor="#A68868" stopOpacity="0.85"/>
          </linearGradient>

          {/* Golden Orbital Arc Gradient */}
          <linearGradient id="memora-orbit-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFF5E6"/>
            <stop offset="30%" stopColor="#E3C39D"/>
            <stop offset="65%" stopColor="#A68868"/>
            <stop offset="100%" stopColor="#4B6382" stopOpacity="0.4"/>
          </linearGradient>

          {/* Subtle Ambient Dropshadows */}
          <filter id="memora-shadow-back" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="-2" dy="8" stdDeviation="8" floodColor="#071739" floodOpacity="0.30"/>
          </filter>
          <filter id="memora-shadow-front" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="-1" dy="6" stdDeviation="7" floodColor="#071739" floodOpacity="0.25"/>
          </filter>
          <filter id="memora-star-glow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="2.5" result="glow"/>
            <feMerge>
              <feMergeNode in="glow"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* Orbital Ring: Back Arc (behind the cards) */}
        <path
          d="M 46,130 C 32,102 58,70 106,52 C 148,36 198,40 220,62 C 226,68 227,74 223,81" 
          stroke="url(#memora-orbit-grad)" 
          strokeWidth="3" 
          strokeLinecap="round" 
          opacity="0.55"
        />

        {/* Back Card: Deep Slate Vault Card (Tilted Left) */}
        <g transform="translate(142, 126) rotate(-14) translate(-48, -66)" filter="url(#memora-shadow-back)">
          <rect x="0" y="0" width="84" height="118" rx="18" fill="url(#memora-card-back)"/>
          <rect x="0.75" y="0.75" width="82.5" height="116.5" rx="17.25" stroke="#A4B5C4" strokeWidth="1.5" strokeOpacity="0.5"/>
          {/* Minimalist Data Accent Lines */}
          <rect x="14" y="24" width="34" height="5" rx="2.5" fill="#A4B5C4" opacity="0.65"/>
          <rect x="14" y="37" width="56" height="3.5" rx="1.75" fill="#A4B5C4" opacity="0.30"/>
          <rect x="14" y="47" width="44" height="3.5" rx="1.75" fill="#A4B5C4" opacity="0.30"/>
        </g>

        {/* Front Card: Frosted Warm Glassmorphic Card (Tilted Right) */}
        <g transform="translate(108, 140) rotate(11) translate(-48, -66)" filter="url(#memora-shadow-front)">
          <rect x="0" y="0" width="86" height="120" rx="18" fill="url(#memora-card-front)"/>
          <rect x="0.75" y="0.75" width="84.5" height="118.5" rx="17.25" stroke="#FFFFFF" strokeWidth="1.75" strokeOpacity="0.9"/>
          {/* Chip / Icon */}
          <rect x="14" y="20" width="22" height="22" rx="7" fill="#071739" fillOpacity="0.20"/>
          <circle cx="25" cy="31" r="5" fill="#071739" fillOpacity="0.6"/>
          {/* Knowledge Structure Lines */}
          <rect x="14" y="52" width="58" height="4.5" rx="2.25" fill="#071739" fillOpacity="0.55"/>
          <rect x="14" y="63" width="46" height="3.5" rx="1.75" fill="#071739" fillOpacity="0.35"/>
          <rect x="14" y="73" width="36" height="3.5" rx="1.75" fill="#071739" fillOpacity="0.25"/>
        </g>

        {/* Orbital Ring: Front Sweeping Arc (in front of cards) */}
        <path
          d="M 44,134 C 54,166 98,194 150,188 C 182,184 206,170 216,150 C 223,136 218,118 202,102" 
          stroke="url(#memora-orbit-grad)" 
          strokeWidth="3.5" 
          strokeLinecap="round"
          filter="url(#memora-star-glow)"
        />

        {/* Orbital Sphere / Pearl Node */}
        <circle cx="202" cy="104" r="7" fill="#E3C39D" filter="url(#memora-star-glow)"/>
        <circle cx="200" cy="102" r="2.5" fill="#FFFFFF"/>

        {/* Brilliant 4-Point Radiant Intelligence Star (Memory Spark) */}
        <g transform="translate(196, 46)" filter="url(#memora-star-glow)">
          <path d="M 0,-18 Q 0,0 18,0 Q 0,0 0,18 Q 0,0 -18,0 Q 0,0 0,-18 Z" fill="#FFFFFF"/>
          <path d="M 0,-12 Q 0,0 12,0 Q 0,0 0,12 Q 0,0 -12,0 Q 0,0 0,-12 Z" fill="#E3C39D"/>
          <circle cx="0" cy="0" r="3" fill="#FFFFFF"/>
        </g>
      </svg>
    </div>
  );
};

export const MindSyncLogo = MemoraLogo;
