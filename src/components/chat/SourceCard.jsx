import React from 'react';
import { FileText, Mic, Image as ImageIcon, FileUp, Link2, ExternalLink } from 'lucide-react';
import { useKnowledge } from '../../context/KnowledgeContext';

export const SourceCard = ({ source }) => {
  const { items, openDetail } = useKnowledge();

  // Find corresponding full item from knowledge base
  const fullItem = items.find((i) => i.id === source.id);

  const handleClick = () => {
    if (fullItem) {
      openDetail(fullItem);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'note': return FileText;
      case 'voice': return Mic;
      case 'image': return ImageIcon;
      case 'document': return FileUp;
      case 'link': return Link2;
      default: return FileText;
    }
  };

  const Icon = getIcon(source.type);

  return (
    <div
      onClick={handleClick}
      className="flex items-center justify-between p-3 rounded-xl bg-palette-cream/60 dark:bg-dark-bg/90 hover:bg-palette-sand/20 dark:hover:bg-dark-hover border border-palette-pale dark:border-dark-border/80 hover:border-palette-slate transition-all cursor-pointer group shadow-sm text-left"
    >
      <div className="flex items-center gap-2.5 min-w-0 mr-2">
        <div className="w-7 h-7 rounded-lg bg-palette-mist/20 border border-palette-mist/40 flex items-center justify-center shrink-0">
          <Icon className="w-3.5 h-3.5 text-palette-slate" />
        </div>
        <div className="truncate">
          <h5 className="text-xs font-semibold text-palette-navy dark:text-white group-hover:text-palette-slate transition-colors truncate">
            {source.title}
          </h5>
          <p className="text-[11px] text-palette-slate/70 dark:text-app-subtle truncate">
            {source.summary || 'Click to view full content'}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {source.relevance && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-palette-sand/40 text-palette-clay border border-palette-clay/30 font-mono font-medium">
            {source.relevance} match
          </span>
        )}
        <ExternalLink className="w-3.5 h-3.5 text-palette-slate group-hover:text-palette-navy transition-colors" />
      </div>
    </div>
  );
};
