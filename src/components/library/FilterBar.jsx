import React from 'react';
import { 
  Grid, 
  List, 
  FileText, 
  Mic, 
  Image as ImageIcon, 
  FileUp, 
  Presentation, 
  FileCode2, 
  Link2, 
  Layers, 
  ArrowUpDown 
} from 'lucide-react';
import { useKnowledge } from '../../context/KnowledgeContext';

export const FilterBar = () => {
  const {
    selectedType,
    setSelectedType,
    selectedSort,
    setSelectedSort,
    viewMode,
    setViewMode,
  } = useKnowledge();

  const typeOptions = [
    { id: 'All', label: 'All Items', icon: Layers },
    { id: 'note', label: 'Notes', icon: FileText },
    { id: 'image', label: 'Images', icon: ImageIcon },
    { id: 'voice', label: 'Audio', icon: Mic },
    { id: 'pdf', label: 'PDFs', icon: FileUp },
    { id: 'ppt', label: 'PPTs', icon: Presentation },
    { id: 'docx', label: 'DOCX', icon: FileCode2 },
    { id: 'link', label: 'Links', icon: Link2 },
  ];

  return (
    <div className="mb-6">
      {/* Controls Row: Type Filters + View Mode + Sort (Topic filter removed per user request) */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Type Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
          {typeOptions.map((opt) => {
            const Icon = opt.icon;
            const active = selectedType === opt.id;
            return (
              <button
                key={opt.id}
                onClick={() => setSelectedType(opt.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${
                  active
                    ? 'bg-palette-navy text-white shadow-sm'
                    : 'bg-white dark:bg-dark-surface/90 text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white border border-palette-border dark:border-dark-border hover:bg-palette-cream dark:hover:bg-dark-hover'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{opt.label}</span>
              </button>
            );
          })}
        </div>

        {/* Right side: Sort & Grid/List view toggle */}
        <div className="flex items-center gap-2 ml-auto">
          {/* Sort Selector */}
          <div className="flex items-center gap-1.5 bg-dark-surface/90 border border-dark-border/80 px-2.5 py-1.5 rounded-xl text-xs">
            <ArrowUpDown className="w-3.5 h-3.5 text-app-subtle" />
            <select
              value={selectedSort}
              onChange={(e) => setSelectedSort(e.target.value)}
              className="bg-transparent text-palette-slate dark:text-app-muted hover:text-palette-navy dark:hover:text-white outline-none cursor-pointer text-xs"
            >
              <option value="newest" className="bg-white dark:bg-dark-card text-palette-navy dark:text-white">Newest First</option>
              <option value="oldest" className="bg-white dark:bg-dark-card text-palette-navy dark:text-white">Oldest First</option>
              <option value="title" className="bg-white dark:bg-dark-card text-palette-navy dark:text-white">Title (A-Z)</option>
            </select>
          </div>

          {/* Grid / List View Toggle */}
          <div className="flex items-center bg-dark-surface/90 border border-dark-border/80 p-0.5 rounded-xl">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                viewMode === 'grid' ? 'bg-dark-hover text-accent-light' : 'text-app-subtle hover:text-white'
              }`}
              title="Grid View"
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                viewMode === 'list' ? 'bg-dark-hover text-accent-light' : 'text-app-subtle hover:text-white'
              }`}
              title="List View"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
