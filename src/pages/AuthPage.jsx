import React, { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { ArrowRight, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { MemoraLogo } from '../components/common/MemoraLogo';

export const AuthPage = () => {
  const { login, signup, isAuthenticated, isLoadingAuth } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // If already authenticated, redirect straight to dashboard
  if (!isLoadingAuth && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleTabSwitch = (signUpMode) => {
    setIsSignUp(signUpMode);
    setErrorMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    const cleanEmail = email.trim();
    const cleanPassword = password.trim();

    if (!cleanEmail || !cleanPassword) {
      setErrorMessage('Please enter both email and password.');
      return;
    }

    if (isSignUp && cleanPassword.length < 6) {
      setErrorMessage('Password must be at least 6 characters long.');
      return;
    }

    setIsLoading(true);

    try {
      if (isSignUp) {
        await signup(name.trim() || undefined, cleanEmail, cleanPassword);
        addToast('Account created successfully!', 'success');
      } else {
        await login(cleanEmail, cleanPassword);
        addToast('Signed in successfully!', 'success');
      }
      navigate('/');
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        'Authentication failed. Please verify your credentials.';
      setErrorMessage(detail);
      addToast(detail, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-palette-cream dark:bg-dark-bg flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background ambient glow orbs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-palette-sand/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-palette-mist/20 rounded-full blur-[140px] pointer-events-none" />

      <div className="w-full max-w-md bg-white dark:bg-dark-surface/90 border border-palette-border dark:border-dark-border/80 rounded-3xl p-8 backdrop-blur-xl shadow-soft-card relative z-10">
        {/* Brand Logo & Name */}
        <div className="flex flex-col items-center text-center mb-8">
          <MemoraLogo size="2xl" className="mb-2" />
          <h1 className="text-2xl font-bold tracking-tight text-palette-navy dark:text-white">
            MEMORA
          </h1>
          <p className="text-[10px] font-bold tracking-widest uppercase text-palette-clay dark:text-palette-sand mt-0.5">
            SAVE ANYTHING. FIND IT ANYTIME.
          </p>
          <p className="text-xs text-palette-slate dark:text-app-muted mt-1">
            {isSignUp ? 'Create your personal knowledge vault' : 'Sign in to access your knowledge vault'}
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex p-1 bg-palette-cream dark:bg-dark-bg rounded-xl border border-palette-pale dark:border-dark-border mb-6">
          <button
            type="button"
            onClick={() => handleTabSwitch(false)}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
              !isSignUp ? 'bg-palette-navy text-white shadow-sm' : 'text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => handleTabSwitch(true)}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
              isSignUp ? 'bg-palette-navy text-white shadow-sm' : 'text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Error Banner */}
        {errorMessage && (
          <div className="flex items-start gap-2.5 p-3.5 mb-5 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-600 dark:text-rose-400 text-xs leading-relaxed">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600 dark:text-rose-400" />
            <span className="flex-1 font-medium">{errorMessage}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignUp && (
            <div>
              <label className="block text-xs font-semibold text-palette-slate dark:text-app-muted uppercase tracking-wider mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                placeholder="e.g. Alex Morgan"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isLoading}
                className="w-full bg-white dark:bg-dark-bg border border-palette-pale dark:border-dark-border focus:border-palette-navy dark:focus:border-palette-sand rounded-xl px-3.5 py-2.5 text-sm text-palette-navy dark:text-white placeholder-app-subtle outline-none transition-colors disabled:opacity-50"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-palette-slate dark:text-app-muted uppercase tracking-wider mb-1.5">
              Email Address
            </label>
            <input
              type="email"
              required
              placeholder="e.g. name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              className="w-full bg-white dark:bg-dark-bg border border-palette-pale dark:border-dark-border focus:border-palette-navy dark:focus:border-palette-sand rounded-xl px-3.5 py-2.5 text-sm text-palette-navy dark:text-white placeholder-app-subtle outline-none transition-colors disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-palette-slate dark:text-app-muted uppercase tracking-wider mb-1.5">
              Password
            </label>
            <input
              type="password"
              required
              placeholder={isSignUp ? 'At least 6 characters' : 'Enter your password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              className="w-full bg-white dark:bg-dark-bg border border-palette-pale dark:border-dark-border focus:border-palette-navy dark:focus:border-palette-sand rounded-xl px-3.5 py-2.5 text-sm text-palette-navy dark:text-white placeholder-app-subtle outline-none transition-colors disabled:opacity-50"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 rounded-xl bg-palette-navy hover:bg-palette-slate text-white text-sm font-semibold active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer mt-3 shadow-lg shadow-palette-navy/20"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>{isSignUp ? 'Creating Account...' : 'Signing In...'}</span>
              </>
            ) : (
              <>
                <span>{isSignUp ? 'Create Knowledge Vault' : 'Access Vault'}</span>
                <ArrowRight className="w-4 h-4 text-palette-sand" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
