import React, { useMemo } from 'react';
import { Star, FolderX, Sparkles } from 'lucide-react';
import { useKnowledge } from '../context/KnowledgeContext';
import { FilterBar } from '../components/library/FilterBar';
import { ContentCard } from '../components/library/ContentCard';

export const FavoritesPage = () => {
  const { 
    items = [], 
    viewMode, 
    searchQuery, 
    selectedType, 
    selectedSort,
    setSelectedType,
    setSearchQuery 
  } = useKnowledge();

  // All favorited items
  const allFavorites = useMemo(() => {
    return (Array.isArray(items) ? items : []).filter((item) => Boolean(item?.favorite));
  }, [items]);

  // Favorited items filtered by search and type, sorted accordingly
  const filteredFavorites = useMemo(() => {
    return allFavorites
      .filter((item) => {
        // Search filter
        if (searchQuery?.trim()) {
          const q = searchQuery.toLowerCase();
          const titleMatch = item.title?.toLowerCase().includes(q);
          const summaryMatch = item.summary?.toLowerCase().includes(q);
          const contentMatch = item.content?.toLowerCase().includes(q);
          const tagMatch = item.tags?.some((t) => t.toLowerCase().includes(q));
          const entityMatch = item.entities?.some((e) => e.toLowerCase().includes(q));
          if (!titleMatch && !summaryMatch && !contentMatch && !tagMatch && !entityMatch) {
            return false;
          }
        }
        // Type filter
        if (selectedType !== 'All' && item.type !== selectedType) {
          return false;
        }
        return true;
      })
      .sort((a, b) => {
        if (selectedSort === 'newest') {
          return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
        }
        if (selectedSort === 'oldest') {
          return new Date(a.createdAt || 0) - new Date(b.createdAt || 0);
        }
        if (selectedSort === 'title') {
          return (a.title || '').localeCompare(b.title || '');
        }
        return 0;
      });
  }, [allFavorites, searchQuery, selectedType, selectedSort]);

  return (
    <div className="space-y-6 pb-16">
      {/* 1. Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-palette-border dark:border-dark-border pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-palette-sand/40 border border-palette-clay/35 flex items-center justify-center text-palette-clay shrink-0">
            <Star className="w-5 h-5 fill-palette-clay text-palette-clay" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-palette-navy dark:text-white flex items-center gap-2">
              <span>Favorites</span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs bg-palette-sand/40 text-palette-clay border border-palette-clay/30 px-3 py-1 rounded-full font-bold flex items-center gap-1.5">
            <Star className="w-3 h-3 fill-palette-clay text-palette-clay" />
            <span>{allFavorites.length} {allFavorites.length === 1 ? 'starred item' : 'starred items'}</span>
          </span>
        </div>
      </div>

      {/* 2. Filter Bar */}
      <FilterBar />

      {/* 3. Items Status Line */}
      <div className="flex items-center justify-between text-xs text-app-subtle">
        <span>
          Showing <strong className="text-palette-navy dark:text-white font-medium">{filteredFavorites.length}</strong> of{' '}
          <strong className="text-palette-clay font-medium">{allFavorites.length}</strong> favorites
          {searchQuery && ` matching "${searchQuery}"`}
          {selectedType !== 'All' && ` of type ${selectedType}`}
        </span>
      </div>

      {/* 4. Grid or List View Render */}
      {filteredFavorites.length > 0 ? (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4'
              : 'space-y-3'
          }
        >
          {filteredFavorites.map((item) => (
            <ContentCard key={item.id} item={item} isList={viewMode === 'list'} />
          ))}
        </div>
      ) : allFavorites.length === 0 ? (
        /* Empty State: No favorites starred yet */
        <div className="glass-card rounded-2xl p-12 text-center max-w-lg mx-auto space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-palette-sand/30 border border-palette-clay/30 flex items-center justify-center mx-auto text-palette-clay">
            <Star className="w-7 h-7 fill-palette-clay/40 text-palette-clay" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-palette-navy dark:text-white">No favorite items yet</h3>
            <p className="text-xs text-app-muted mt-1 leading-relaxed">
              Click the star icon (<Star className="w-3 h-3 inline text-palette-clay fill-palette-clay" />) on any card in the Dashboard or Library to pin it to your favorites.
            </p>
          </div>
        </div>
      ) : (
        /* Empty State: Favorites exist but filters/search returned zero */
        <div className="glass-card rounded-2xl p-12 text-center max-w-lg mx-auto space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-palette-cream dark:bg-dark-surface border border-palette-border dark:border-dark-border flex items-center justify-center mx-auto text-app-subtle">
            <FolderX className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-palette-navy dark:text-white">No matching favorites found</h3>
            <p className="text-xs text-app-muted mt-1">
              No favorited items match the active filter or search query.
            </p>
          </div>
          <button
            onClick={() => {
              setSelectedType('All');
              if (setSearchQuery) setSearchQuery('');
            }}
            className="px-4 py-2 rounded-xl bg-palette-navy hover:bg-palette-slate text-white text-xs font-semibold cursor-pointer transition-colors"
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
};
