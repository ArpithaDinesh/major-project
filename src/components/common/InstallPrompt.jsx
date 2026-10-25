import React, { useState } from 'react';
import { Download, Sparkles, X, Smartphone } from 'lucide-react';
import { usePWAInstall } from '../../hooks/usePWAInstall';

export const InstallPrompt = () => {
  const { isInstallable, promptInstall } = usePWAInstall();
  const [dismissed, setDismissed] = useState(false);

  if (!isInstallable || dismissed) return null;

  return (
    <div className="relative overflow-hidden mb-6 p-4 rounded-2xl bg-gradient-to-r from-accent/15 via-dark-card to-accent-teal/10 border border-accent/30 shadow-glow-sm">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-accent/20 border border-accent/40 flex items-center justify-center shrink-0">
            <Smartphone className="w-5 h-5 text-accent-light" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-palette-navy dark:text-white flex items-center gap-2">
              Install Memora Progressive Web App
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-accent/20 text-accent-light font-mono">Offline Ready</span>
            </h4>
            <p className="text-xs text-app-muted mt-0.5">
              Enjoy zero-latency offline note capture, instant voice memos, and native desktop/mobile experience.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-center">
          <button
            onClick={() => setDismissed(true)}
            className="px-3 py-1.5 rounded-xl text-xs font-medium text-palette-slate dark:text-app-subtle hover:text-palette-navy dark:hover:text-white transition-colors cursor-pointer"
          >
            Dismiss
          </button>
          <button
            onClick={promptInstall}
            className="flex items-center gap-2 px-4 py-1.5 rounded-xl bg-accent hover:bg-accent-hover text-white text-xs font-semibold shadow-glow-sm hover:shadow-glow-md transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Install App</span>
          </button>
        </div>
      </div>
    </div>
  );
};
