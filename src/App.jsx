import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { KnowledgeProvider } from './context/KnowledgeContext';
import { ToastProvider } from './context/ToastContext';

// Components
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { Sidebar } from './components/common/Sidebar';
import { Header } from './components/common/Header';
import { MobileNav } from './components/common/MobileNav';
import { BottomCaptureDock } from './components/capture/BottomCaptureDock';
import { CaptureModal } from './components/capture/CaptureModal';
import { DetailModal } from './components/library/DetailModal';

// Pages
import { AuthPage } from './pages/AuthPage';
import { DashboardPage } from './pages/DashboardPage';
import { LibraryPage } from './pages/LibraryPage';
import { FavoritesPage } from './pages/FavoritesPage';
import { ChatPage } from './pages/ChatPage';
import { RemindersPage } from './pages/RemindersPage';
import { SettingsPage } from './pages/SettingsPage';

// Main Application Layout
const AppLayout = () => {
  const { isAuthenticated, isLoadingAuth } = useAuth();

  if (isLoadingAuth) {
    return (
      <div className="min-h-screen bg-palette-cream dark:bg-dark-bg flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-palette-navy dark:border-palette-sand border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-palette-cream dark:bg-dark-bg text-app-text flex relative selection:bg-palette-sand/40 selection:text-palette-navy">
      {/* 1. Left Vertical Hover-Expand Sidebar (Icons only -> expands on hover) */}
      <Sidebar />
      
      {/* 2. Main Canvas (offset by fixed sidebar width 256px / pl-64 on md+) */}
      <div className="flex-1 flex flex-col min-w-0 md:pl-64 transition-all duration-300">
        {/* Top Header with Search, Status, and Controls */}
        <Header />

        {/* Core Page Content */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-32 md:pb-24">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="/favorites" element={<FavoritesPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/reminders" element={<RemindersPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Bottom Tab Bar for Mobile screens */}
        <MobileNav />
      </div>

      {/* 3. Prominent Bottom-Right Capture Action Button (Bigger, glowing + button opening radially with just logos) */}
      <BottomCaptureDock />

      {/* 4. Global Modals */}
      <CaptureModal />
      <DetailModal />
    </div>
  );
};

export const App = () => {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <ToastProvider>
          <AuthProvider>
            <KnowledgeProvider>
              <Routes>
                <Route path="/login" element={<AuthPage />} />
                <Route path="/*" element={<AppLayout />} />
              </Routes>
            </KnowledgeProvider>
          </AuthProvider>
        </ToastProvider>
      </ErrorBoundary>
    </BrowserRouter>
  );
};

export default App;
