import React from 'react';
import { AlertTriangle, RotateCcw, Home } from 'lucide-react';
import { MindSyncLogo } from './MindSyncLogo';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('MindSync React ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-palette-cream dark:bg-dark-bg text-palette-navy dark:text-white flex flex-col items-center justify-center p-6 text-center select-none">
          <div className="w-full max-w-md p-6 sm:p-8 rounded-3xl bg-white dark:bg-dark-card border border-palette-border dark:border-dark-border shadow-soft-card flex flex-col items-center animate-fadeIn">
            <MindSyncLogo size="lg" className="mb-4" />
            
            <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-600 dark:text-rose-400 mb-3">
              <AlertTriangle className="w-6 h-6" />
            </div>

            <h2 className="text-xl font-bold tracking-tight mb-1 text-palette-navy dark:text-white">
              Something went wrong
            </h2>
            <p className="text-xs text-palette-slate dark:text-app-muted mb-4 max-w-xs">
              MindSync encountered an unexpected rendering issue. Don't worry, your knowledge vault is safe.
            </p>

            {this.state.error?.message && (
              <div className="w-full p-3 rounded-xl bg-palette-cream dark:bg-dark-bg border border-palette-pale dark:border-dark-border text-left font-mono text-[11px] text-rose-600 dark:text-rose-300 break-words mb-5 max-h-32 overflow-y-auto">
                {this.state.error.message}
              </div>
            )}

            <div className="flex items-center gap-3 w-full">
              <button
                onClick={this.handleReload}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-palette-navy hover:bg-palette-slate text-white text-xs font-semibold shadow-sm transition-all cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reload App</span>
              </button>
              <button
                onClick={this.handleReset}
                className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-white dark:bg-dark-surface border border-palette-border dark:border-dark-border hover:border-palette-slate text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white text-xs font-semibold transition-all cursor-pointer"
              >
                <Home className="w-3.5 h-3.5" />
                <span>Go Home</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
