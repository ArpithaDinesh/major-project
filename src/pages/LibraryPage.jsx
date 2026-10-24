import React from 'react';
import { Library, FolderX } from 'lucide-react';
import { useKnowledge } from '../context/KnowledgeContext';
import { FilterBar } from '../components/library/FilterBar';
import { ContentCard } from '../components/library/ContentCard';

export const LibraryPage = () => {
  const { filteredItems, viewMode, searchQuery, selectedType } = useKnowledge();

  return (
    <div className="space-y-6 pb-16">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-palette-navy dark:text-white flex items-center gap-2">
          <Library className="w-6 h-6 text-palette-slate" />
          <span>Knowledge Base</span>
        </h1>
      </div>

      {/* Filter Bar (Without topic filters) */}
      <FilterBar />

      {/* Items Section Header */}
      <div className="flex items-center justify-between text-xs text-palette-slate dark:text-app-subtle">
        <span>
          Showing <strong className="text-palette-navy dark:text-white font-medium">{filteredItems.length}</strong> items
          {searchQuery && ` matching "${searchQuery}"`}
          {selectedType !== 'All' && ` of type ${selectedType}`}
        </span>
      </div>

      {/* Grid or List View Render */}
      {filteredItems.length > 0 ? (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4'
              : 'space-y-3'
          }
        >
          {filteredItems.map((item) => (
            <ContentCard key={item.id} item={item} isList={viewMode === 'list'} />
          ))}
        </div>
      ) : (
        /* Empty State */
        <div className="glass-card rounded-2xl p-12 text-center max-w-lg mx-auto space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-palette-cream dark:bg-dark-surface border border-palette-border dark:border-dark-border flex items-center justify-center mx-auto text-app-subtle">
            <FolderX className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-palette-navy dark:text-white">No knowledge items found</h3>
            <p className="text-xs text-palette-slate dark:text-app-muted mt-1">
              Try adjusting your search query, clearing filters, or capture something new using the floating + button.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
