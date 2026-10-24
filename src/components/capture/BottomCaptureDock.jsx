import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  Plus, 
  FileText, 
  Image as ImageIcon, 
  Mic, 
  FileUp, 
  Presentation, 
  FileCode2, 
  Link2 
} from 'lucide-react';
import { useKnowledge } from '../../context/KnowledgeContext';

export const BottomCaptureDock = () => {
  const location = useLocation();
  const { openCapture } = useKnowledge();
  const [isOpen, setIsOpen] = useState(false);
  const dockRef = useRef(null);

  // Close menu on click outside or Escape key
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dockRef.current && !dockRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  // The 7 requested upload/capture modalities with just their logos
  const captureOptions = [
    {
      id: 'note',
      label: 'Text Note',
      icon: FileText,
      color: 'text-palette-slate group-hover:text-palette-navy',
      bg: 'hover:bg-palette-cream',
      border: 'border-palette-pale hover:border-palette-slate',
    },
    {
      id: 'image',
      label: 'Image & OCR',
      icon: ImageIcon,
      color: 'text-palette-clay group-hover:text-palette-navy',
      bg: 'hover:bg-palette-cream',
      border: 'border-palette-pale hover:border-palette-clay',
    },
    {
      id: 'voice',
      label: 'Audio Memo',
      icon: Mic,
      color: 'text-palette-slate group-hover:text-palette-navy',
      bg: 'hover:bg-palette-cream',
      border: 'border-palette-pale hover:border-palette-slate',
    },
    {
      id: 'pdf',
      label: 'PDF Document',
      icon: FileUp,
      color: 'text-palette-navy group-hover:text-palette-slate',
      bg: 'hover:bg-palette-cream',
      border: 'border-palette-pale hover:border-palette-navy',
    },
    {
      id: 'ppt',
      label: 'PPT Slides',
      icon: Presentation,
      color: 'text-palette-clay group-hover:text-palette-navy',
      bg: 'hover:bg-palette-cream',
      border: 'border-palette-pale hover:border-palette-clay',
    },
    {
      id: 'docx',
      label: 'Word DOCX',
      icon: FileCode2,
      color: 'text-palette-slate group-hover:text-palette-navy',
      bg: 'hover:bg-palette-cream',
      border: 'border-palette-pale hover:border-palette-slate',
    },
    {
      id: 'link',
      label: 'Web Link',
      icon: Link2,
      color: 'text-palette-clay group-hover:text-palette-navy',
      bg: 'hover:bg-palette-cream',
      border: 'border-palette-pale hover:border-palette-clay',
    },
  ];

  const handleSelectOption = (optionId) => {
    setIsOpen(false);
    openCapture(optionId);
  };

  // Radial calculation: 7 items fanned out in a circular arc upward and leftward from bottom-right
  const radius = 135; // in pixels
  const startAngle = 80;
  const endAngle = 200;
  const totalItems = captureOptions.length;

  // Hide the floating capture/input button on AI chat page and settings page
  const isHidden = ['/chat', '/settings'].some((path) => location.pathname.startsWith(path));
  if (isHidden) {
    return null;
  }

  return (
    <>
      {/* Subtle backdrop overlay when circular menu is open */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="fixed inset-0 z-40 bg-black/45 backdrop-blur-[2px] transition-opacity duration-300"
          aria-hidden="true"
        />
      )}

      {/* Floating Capture Container positioned on the bottom right side */}
      <div 
        ref={dockRef} 
        className="fixed bottom-7 right-7 sm:bottom-8 sm:right-8 z-50 flex items-center justify-center pointer-events-none"
      >
        <div className="relative flex items-center justify-center pointer-events-auto">
          
          {/* Circular fanning option icons */}
          {captureOptions.map((opt, idx) => {
            const Icon = opt.icon;
            
            // Calculate angle and position
            const angleDeg = startAngle + ((endAngle - startAngle) / (totalItems - 1)) * idx;
            const angleRad = (angleDeg * Math.PI) / 180;
            const x = Math.round(radius * Math.cos(angleRad));
            const y = Math.round(-radius * Math.sin(angleRad));

            return (
              <div
                key={opt.id}
                style={{
                  transform: isOpen
                    ? `translate(${x}px, ${y}px) scale(1)`
                    : 'translate(0px, 0px) scale(0)',
                  opacity: isOpen ? 1 : 0,
                  transitionDelay: isOpen ? `${idx * 28}ms` : `${(totalItems - 1 - idx) * 16}ms`,
                  transitionProperty: 'transform, opacity',
                  transitionDuration: '320ms',
                  transitionTimingFunction: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
                  pointerEvents: isOpen ? 'auto' : 'none',
                }}
                className="absolute z-50 group flex flex-col items-center"
              >
                {/* Floating Tooltip Label on hover */}
                <div className="absolute -top-7 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none transform -translate-y-1 group-hover:translate-y-0">
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-white dark:bg-dark-card text-palette-navy dark:text-white border border-palette-border dark:border-dark-border shadow-soft-card">
                    {opt.label}
                  </span>
                </div>

                {/* Just the circular logo button */}
                <button
                  onClick={() => handleSelectOption(opt.id)}
                  aria-label={opt.label}
                  className={`w-12 h-12 rounded-full bg-white dark:bg-dark-card/95 backdrop-blur-xl border ${opt.border} ${opt.bg} shadow-soft-card flex items-center justify-center transition-all duration-200 hover:scale-110 active:scale-95 cursor-pointer`}
                >
                  <Icon className={`w-5 h-5 ${opt.color} transition-transform group-hover:scale-110`} />
                </button>
              </div>
            );
          })}

          {/* Floating '+' Trigger Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            aria-label={isOpen ? 'Close Capture Menu' : 'Capture Knowledge'}
            title={isOpen ? 'Close' : 'Capture Knowledge'}
            className={`capture-fab-btn relative z-50 w-14 h-14 sm:w-15 sm:h-15 rounded-full flex items-center justify-center transition-all duration-300 cursor-pointer border-2 shadow-lg ${
              isOpen 
                ? 'rotate-45 bg-palette-slate text-white border-palette-sand' 
                : 'bg-palette-navy hover:bg-palette-slate text-white border-palette-sand hover:scale-105'
            }`}
          >
            <Plus className="w-7 h-7 sm:w-8 sm:h-8 transition-transform duration-300 text-white" strokeWidth={2.5} />
          </button>

        </div>
      </div>
    </>
  );
};
