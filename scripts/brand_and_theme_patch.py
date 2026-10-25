import os
import re

def patch_file(path, replacements):
    if not os.path.exists(path):
        print(f"Skipping {path}: not found")
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    for old, new in replacements:
        content = content.replace(old, new)
    if content != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully patched {path}")
    else:
        print(f"No changes made to {path} (already up to date)")

# 1. ChatBubble.jsx
patch_file('src/components/chat/ChatBubble.jsx', [
    ("import { MindSyncLogo } from '../common/MindSyncLogo';", "import { MemoraLogo } from '../common/MemoraLogo';"),
    ('<MindSyncLogo size="sm" className="mt-0.5" />', '<MemoraLogo size="sm" className="mt-0.5" />'),
    ('<strong key={pIdx} className="text-white font-semibold">', '<strong key={pIdx} className="text-palette-navy dark:text-white font-bold">'),
    ('text-sm text-app-text my-0.5', 'text-sm text-palette-navy dark:text-white my-0.5'),
    ('text-sm text-app-text my-1 pl-2 border-l-2 border-accent/40', 'text-sm text-palette-navy dark:text-white my-1 pl-2 border-l-2 border-palette-clay/60 dark:border-accent/40'),
    ('text-sm text-app-text my-1 leading-relaxed', 'text-sm text-palette-navy dark:text-white my-1 leading-relaxed'),
])

# 2. CaptureModal.jsx
patch_file('src/components/capture/CaptureModal.jsx', [
    ('MindSync Ingestion Engine', 'Memora Ingestion Engine'),
    ('Synchronizing with MindSync Vault...', 'Synchronizing with Memora Vault...'),
    ('"Markdown Notes", "MindSync Knowledge", category', '"Markdown Notes", "Memora Knowledge", category'),
    ('[Recorded via MindSync audio engine]', '[Recorded via Memora audio engine]'),
    ('<h3 className="text-base font-bold text-white leading-tight">Capture Knowledge</h3>', '<h3 className="text-base font-bold text-palette-navy dark:text-white leading-tight">Capture Knowledge</h3>'),
    ('<h4 className="text-lg font-bold text-white mb-2">', '<h4 className="text-lg font-bold text-palette-navy dark:text-white mb-2">'),
    ('className="w-full bg-dark-bg/80 border border-dark-border focus:border-accent rounded-xl p-3 text-sm text-white placeholder-app-subtle outline-none resize-none"', 'className="w-full bg-white dark:bg-dark-bg/80 border border-palette-border dark:border-dark-border focus:border-palette-navy dark:focus:border-accent rounded-xl p-3 text-sm text-palette-navy dark:text-white placeholder-palette-slate/60 dark:placeholder-app-subtle outline-none resize-none"'),
    ('className="w-full bg-dark-bg/80 border border-dark-border focus:border-accent rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-app-subtle outline-none"', 'className="w-full bg-white dark:bg-dark-bg/80 border border-palette-border dark:border-dark-border focus:border-palette-navy dark:focus:border-accent rounded-xl px-3.5 py-2.5 text-sm text-palette-navy dark:text-white placeholder-palette-slate/60 dark:placeholder-app-subtle outline-none"'),
])

# 3. InstallPrompt.jsx
patch_file('src/components/common/InstallPrompt.jsx', [
    ('Install MindSync Progressive Web App', 'Install Memora Progressive Web App'),
    ('<h4 className="text-sm font-semibold text-white flex items-center gap-2">', '<h4 className="text-sm font-semibold text-palette-navy dark:text-white flex items-center gap-2">'),
    ('text-app-subtle hover:text-white transition-colors cursor-pointer', 'text-palette-slate dark:text-app-subtle hover:text-palette-navy dark:hover:text-white transition-colors cursor-pointer'),
])

# 4. ErrorBoundary.jsx
patch_file('src/components/common/ErrorBoundary.jsx', [
    ("import { MindSyncLogo } from './MindSyncLogo';", "import { MemoraLogo } from './MemoraLogo';"),
    ('<MindSyncLogo size="lg" className="mb-4" />', '<MemoraLogo size="lg" className="mb-4" />'),
    ("console.error('MindSync React ErrorBoundary caught an error:', error, errorInfo);", "console.error('Memora React ErrorBoundary caught an error:', error, errorInfo);"),
    ("MindSync encountered an unexpected rendering issue. Don't worry, your knowledge vault is safe.", "Memora encountered an unexpected rendering issue. Don't worry, your knowledge vault is safe."),
])

# 5. AddReminderModal.jsx
patch_file('src/components/reminders/AddReminderModal.jsx', [
    ('className="w-full max-w-md bg-dark-card border border-dark-border rounded-2xl shadow-2xl p-6"', 'className="w-full max-w-md bg-white dark:bg-dark-card border border-palette-border dark:border-dark-border rounded-2xl shadow-soft-card p-6"'),
    ('<h3 className="text-base font-bold text-white">Add Reminder</h3>', '<h3 className="text-base font-bold text-palette-navy dark:text-white">Add Reminder</h3>'),
    ('text-app-subtle hover:text-white p-1', 'text-palette-slate dark:text-app-subtle hover:text-palette-navy dark:hover:text-white p-1 cursor-pointer'),
    ('text-app-muted uppercase tracking-wider', 'text-palette-slate dark:text-app-muted uppercase tracking-wider'),
    ('className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-app-subtle outline-none"', 'className="w-full bg-white dark:bg-dark-bg border border-palette-border dark:border-dark-border focus:border-palette-navy dark:focus:border-accent rounded-xl px-3.5 py-2.5 text-sm text-palette-navy dark:text-white placeholder-palette-slate/60 dark:placeholder-app-subtle outline-none"'),
    ('className="w-full bg-dark-bg border border-dark-border focus:border-accent rounded-xl px-3 py-2 text-xs text-white outline-none"', 'className="w-full bg-white dark:bg-dark-bg border border-palette-border dark:border-dark-border focus:border-palette-navy dark:focus:border-accent rounded-xl px-3 py-2 text-xs text-palette-navy dark:text-white outline-none"'),
    ('text-app-muted hover:text-white', 'text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white cursor-pointer'),
    ('bg-accent hover:bg-accent-hover text-white text-xs font-semibold shadow-glow-sm', 'bg-palette-navy hover:bg-palette-slate text-white text-xs font-semibold shadow-sm cursor-pointer'),
])

# 6. DetailModal.jsx
patch_file('src/components/library/DetailModal.jsx', [
    ('className="w-full max-w-3xl bg-dark-card border border-dark-border rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]"', 'className="w-full max-w-3xl bg-white dark:bg-dark-card border border-palette-border dark:border-dark-border rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]"'),
    ('className="flex items-center justify-between px-6 py-4 border-b border-dark-border/80 bg-dark-surface/80"', 'className="flex items-center justify-between px-6 py-4 border-b border-palette-border dark:border-dark-border/80 bg-palette-cream/70 dark:bg-dark-surface/80"'),
    ('<h3 className="text-base font-bold text-white truncate">{item.title}</h3>', '<h3 className="text-base font-bold text-palette-navy dark:text-white truncate">{item.title}</h3>'),
    ('className="text-white font-medium break-words font-mono"', 'className="text-palette-navy dark:text-white font-medium break-words font-mono"'),
    ('text-app-subtle hover:text-white', 'text-palette-slate dark:text-app-subtle hover:text-palette-navy dark:hover:text-white'),
])

# 7. ChatPage.jsx
patch_file('src/pages/ChatPage.jsx', [
    ('<h1 className="text-base font-bold text-white">', '<h1 className="text-base font-bold text-palette-navy dark:text-white">'),
    ('border-dark-border hover:bg-dark-hover text-app-subtle hover:text-white', 'border-palette-border dark:border-dark-border hover:bg-palette-cream dark:hover:bg-dark-hover text-palette-slate dark:text-app-subtle hover:text-palette-navy dark:hover:text-white'),
    ('bg-dark-surface hover:bg-dark-hover border border-dark-border/80 hover:border-accent/40 text-app-muted hover:text-white', 'bg-white dark:bg-dark-surface hover:bg-palette-cream dark:hover:bg-dark-hover border border-palette-border dark:border-dark-border hover:border-palette-slate text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white'),
    ('className="w-full bg-dark-surface/90 border border-dark-border focus:border-accent/70 focus:ring-1 focus:ring-accent/40 rounded-2xl pl-4 pr-24 py-3.5 text-sm text-white placeholder-app-subtle transition-all outline-none"', 'className="w-full bg-white dark:bg-dark-surface/90 border border-palette-border dark:border-dark-border focus:border-palette-navy dark:focus:border-accent/70 rounded-2xl pl-4 pr-24 py-3.5 text-sm text-palette-navy dark:text-white placeholder-palette-slate/60 dark:placeholder-app-subtle transition-all outline-none shadow-soft-card"'),
    ('className="absolute right-2 px-4 py-2 rounded-xl bg-accent hover:bg-accent-hover text-white text-xs font-semibold disabled:opacity-40 transition-all flex items-center gap-1.5 cursor-pointer"', 'className="absolute right-2 px-4 py-2 rounded-xl bg-palette-navy hover:bg-palette-slate text-white text-xs font-semibold disabled:opacity-40 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"'),
])

# 8. FilterBar.jsx
patch_file('src/components/library/FilterBar.jsx', [
    ("active\n                    ? 'bg-accent text-white'\n                    : 'bg-dark-surface/90 text-app-muted hover:text-white border border-dark-border/80 hover:bg-dark-hover'",
     "active\n                    ? 'bg-palette-navy text-white shadow-sm'\n                    : 'bg-white dark:bg-dark-surface/90 text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white border border-palette-border dark:border-dark-border hover:bg-palette-cream dark:hover:bg-dark-hover'"),
    ('<select\n              value={selectedSort}\n              onChange={(e) => setSelectedSort(e.target.value)}\n              className="bg-transparent text-app-muted hover:text-white outline-none cursor-pointer text-xs"\n            >',
     '<select\n              value={selectedSort}\n              onChange={(e) => setSelectedSort(e.target.value)}\n              className="bg-transparent text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white outline-none cursor-pointer text-xs"\n            >'),
    ('className="bg-dark-card text-white"', 'className="bg-white dark:bg-dark-card text-palette-navy dark:text-white"'),
])

print("All file patches completed.")
