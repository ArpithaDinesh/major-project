import React, { useState } from 'react';
import { Sparkles, User, Copy, Check } from 'lucide-react';
import { SourceCard } from './SourceCard';
import { useAuth } from '../../context/AuthContext';
import { MindSyncLogo } from '../common/MindSyncLogo';

export const ChatBubble = ({ message }) => {
  const { user } = useAuth();
  const isUser = message.sender === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Simple markdown-to-html line formatter
  const renderFormattedText = (text) => {
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      // Bold highlight formatting: **text**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      const formattedParts = parts.map((part, pIdx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return (
            <strong key={pIdx} className="text-white font-semibold">
              {part.slice(2, -2)}
            </strong>
          );
        }
        return part;
      });

      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        return (
          <li key={idx} className="ml-4 list-disc text-sm text-app-text my-0.5">
            {formattedParts}
          </li>
        );
      }

      if (/^\d+\.\s/.test(line.trim())) {
        return (
          <div key={idx} className="text-sm text-app-text my-1 pl-2 border-l-2 border-accent/40">
            {formattedParts}
          </div>
        );
      }

      return (
        <p key={idx} className="text-sm text-app-text my-1 leading-relaxed">
          {formattedParts}
        </p>
      );
    });
  };

  if (isUser) {
    return (
      <div className="flex items-start justify-end gap-3 max-w-2xl ml-auto animate-slideUp">
        <div className="bg-palette-navy text-white px-4 py-3 rounded-2xl rounded-tr-sm shadow-sm max-w-xl text-sm leading-relaxed">
          {message.text}
        </div>
        <img
          src={user?.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&q=80"}
          alt="User"
          className="w-8 h-8 rounded-full object-cover border border-palette-slate/40 shrink-0 mt-0.5"
        />
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 max-w-3xl mr-auto animate-slideUp">
      <MindSyncLogo size="sm" className="mt-0.5" />

      <div className="flex-1 bg-white dark:bg-dark-card border border-palette-border dark:border-dark-border rounded-2xl rounded-tl-sm p-4 sm:p-5 shadow-soft-card relative group">
        {/* Copy button */}
        <button
          onClick={handleCopy}
          className="absolute top-3 right-3 p-1.5 rounded-lg text-palette-slate dark:text-app-subtle hover:text-palette-navy dark:hover:text-white hover:bg-palette-cream dark:hover:bg-dark-hover opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
          title="Copy response"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
        </button>

        {/* Message Body */}
        <div className="space-y-1">
          {renderFormattedText(message.text)}
        </div>

        {/* Source Citations */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-3.5 border-t border-palette-border dark:border-dark-border/70 space-y-2">
            <span className="text-[11px] font-semibold text-palette-slate dark:text-app-subtle uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-palette-clay" />
              Retrieved Knowledge Sources ({message.sources.length})
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {message.sources.map((src, idx) => (
                <SourceCard key={idx} source={src} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
