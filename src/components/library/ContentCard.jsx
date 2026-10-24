import React from 'react';
import { 
  FileText, 
  Mic, 
  Image as ImageIcon, 
  FileUp, 
  Presentation, 
  FileCode2, 
  Link2, 
  Star, 
  Calendar, 
  ExternalLink, 
  Clock, 
  Sparkles 
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useKnowledge } from '../../context/KnowledgeContext';

export const ContentCard = ({ item, isList = false, showTags = true, showCategory = true }) => {
  const { openDetail, toggleFavorite } = useKnowledge();

  const getTypeMeta = (type) => {
    switch (type) {
      case 'note':
        return { icon: FileText, label: 'Note', color: 'text-palette-slate', bg: 'bg-palette-slate/10', border: 'border-palette-slate/20' };
      case 'voice':
        return { icon: Mic, label: 'Audio', color: 'text-palette-navy dark:text-palette-sand', bg: 'bg-palette-sand/20', border: 'border-palette-sand/40' };
      case 'image':
        return { icon: ImageIcon, label: 'Image / OCR', color: 'text-palette-clay', bg: 'bg-palette-sand/30', border: 'border-palette-clay/30' };
      case 'pdf':
      case 'document':
        return { icon: FileUp, label: 'PDF Doc', color: 'text-palette-navy dark:text-palette-mist', bg: 'bg-palette-mist/20', border: 'border-palette-mist/40' };
      case 'ppt':
        return { icon: Presentation, label: 'Presentation', color: 'text-palette-clay', bg: 'bg-palette-sand/30', border: 'border-palette-clay/30' };
      case 'docx':
        return { icon: FileCode2, label: 'DOCX Document', color: 'text-palette-slate', bg: 'bg-palette-slate/10', border: 'border-palette-slate/20' };
      case 'link':
        return { icon: Link2, label: 'Web Link', color: 'text-palette-slate', bg: 'bg-palette-mist/20', border: 'border-palette-mist/40' };
      default:
        return { icon: FileText, label: 'Item', color: 'text-palette-slate', bg: 'bg-palette-cream', border: 'border-palette-pale' };
    }
  };

  const meta = getTypeMeta(item.type);
  const Icon = meta.icon;

  let timeAgo = '';
  try {
    timeAgo = formatDistanceToNow(new Date(item.createdAt), { addSuffix: true });
  } catch {
    timeAgo = 'Recently';
  }

  // LIST VIEW LAYOUT
  if (isList) {
    return (
      <div 
        onClick={() => openDetail(item)}
        className="glass-card glass-card-hover rounded-xl p-4 flex items-center justify-between gap-4 cursor-pointer group"
      >
        <div className="flex items-center gap-3.5 min-w-0">
          <div className={`w-9 h-9 rounded-lg ${meta.bg} ${meta.border} border flex items-center justify-center shrink-0`}>
            <Icon className={`w-4 h-4 ${meta.color}`} />
          </div>
          <div className="min-w-0">
            <h4 className="text-sm font-semibold text-palette-navy dark:text-white group-hover:text-palette-slate transition-colors truncate">
              {item.title}
            </h4>
            <p className="text-xs text-palette-slate dark:text-app-muted truncate mt-0.5">{item.summary}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 shrink-0">
          {item.detectedEvents?.length > 0 && (
            <span className="hidden sm:flex items-center gap-1 text-[11px] font-medium text-palette-navy dark:text-white bg-palette-sand/30 border border-palette-clay/30 px-2 py-0.5 rounded-full">
              <Calendar className="w-3 h-3 text-palette-clay" />
              Event
            </span>
          )}
          <span className="text-xs text-app-subtle hidden md:inline">{timeAgo}</span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              toggleFavorite(item.id);
            }}
            className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
              item.favorite ? 'text-palette-clay' : 'text-palette-slate/50 hover:text-palette-navy dark:hover:text-white'
            }`}
          >
            <Star className={`w-4 h-4 ${item.favorite ? 'fill-palette-clay text-palette-clay' : ''}`} />
          </button>
        </div>
      </div>
    );
  }

  // GRID CARD LAYOUT
  return (
    <div
      onClick={() => openDetail(item)}
      className="glass-card glass-card-hover rounded-2xl p-5 flex flex-col justify-between cursor-pointer group relative overflow-hidden"
    >
      <div>
        {/* Top Header: Badge & Favorite */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <div className={`w-7 h-7 rounded-lg ${meta.bg} ${meta.border} border flex items-center justify-center`}>
              <Icon className={`w-3.5 h-3.5 ${meta.color}`} />
            </div>
            <span className={`text-[11px] font-medium ${meta.color}`}>{meta.label}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleFavorite(item.id);
              }}
              className={`p-1 rounded-lg transition-colors cursor-pointer ${
                item.favorite ? 'text-palette-clay' : 'text-palette-slate/50 hover:text-palette-navy dark:hover:text-white'
              }`}
            >
              <Star className={`w-4 h-4 ${item.favorite ? 'fill-palette-clay text-palette-clay' : ''}`} />
            </button>
          </div>
        </div>

        {/* Thumbnail Preview for Images */}
        {item.type === 'image' && item.imageUrl && (
          <div className="w-full h-32 rounded-xl overflow-hidden mb-3 border border-palette-border dark:border-dark-border bg-palette-cream dark:bg-dark-bg">
            <img
              src={item.imageUrl}
              alt={item.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          </div>
        )}

        {/* Title */}
        <h4 className="text-sm font-semibold text-palette-navy dark:text-white group-hover:text-palette-slate transition-colors line-clamp-1 mb-1.5">
          {item.title}
        </h4>

        {/* AI Summary */}
        <p className="text-xs text-palette-slate dark:text-app-muted line-clamp-2 leading-relaxed mb-4">
          {item.summary}
        </p>
      </div>

      {/* Footer Details: Tags, Events, Timestamp */}
      <div className="pt-3 border-t border-palette-border dark:border-dark-border/60 space-y-2.5">
        {/* Detected Action Items / Deadlines */}
        {item.detectedEvents?.length > 0 && (
          <div className="flex items-center gap-1.5 text-[11px] text-palette-navy dark:text-palette-sand bg-palette-sand/30 border border-palette-clay/30 px-2.5 py-1 rounded-lg">
            <Calendar className="w-3.5 h-3.5 shrink-0 text-palette-clay" />
            <span className="truncate font-medium">{item.detectedEvents[0].title}</span>
          </div>
        )}

        {/* Tags & Time */}
        <div className="flex items-center justify-between text-xs">
          {showTags && item.tags?.length > 0 ? (
            <div className="flex items-center gap-1.5 overflow-hidden">
              {item.tags.slice(0, 2).map((tag, i) => (
                <span
                  key={i}
                  className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-palette-cream dark:bg-dark-bg text-palette-slate dark:text-app-subtle border border-palette-pale dark:border-dark-border truncate"
                >
                  #{tag}
                </span>
              ))}
              {item.tags.length > 2 && (
                <span className="text-[10px] text-app-subtle">+{item.tags.length - 2}</span>
              )}
            </div>
          ) : (
            <div />
          )}

          <div className="flex items-center gap-1 text-[11px] text-app-subtle shrink-0">
            <Clock className="w-3 h-3" />
            <span>{timeAgo}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
