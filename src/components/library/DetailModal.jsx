import React, { useState, useEffect } from 'react';
import { 
  X, 
  Trash2, 
  Star, 
  ExternalLink, 
  FileText, 
  Mic, 
  Image as ImageIcon, 
  FileUp, 
  Presentation, 
  FileCode2, 
  Link2, 
  Sparkles, 
  Play, 
  Pause, 
  Calendar, 
  Tag, 
  Layers, 
  Copy, 
  Check, 
  CheckCircle2,
  Edit3,
  Save,
  Clock,
  ShieldAlert,
  DollarSign,
  Ticket,
  MapPin,
  Building,
  Award,
  Utensils,
  Plus
} from 'lucide-react';
import { format } from 'date-fns';
import { useKnowledge } from '../../context/KnowledgeContext';
import { useToast } from '../../context/ToastContext';

export const DetailModal = () => {
  const { 
    selectedItemDetail, 
    closeDetail, 
    deleteItem, 
    toggleFavorite, 
    updateItem, 
    confirmReminder 
  } = useKnowledge();
  const { addToast } = useToast();
  
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioProgress, setAudioProgress] = useState(35);
  const [copied, setCopied] = useState(false);

  // In-place editing mode state (Requirement 13)
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [editSummary, setEditSummary] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editCategoryData, setEditCategoryData] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [confirmingReminderId, setConfirmingReminderId] = useState(null);

  useEffect(() => {
    if (selectedItemDetail) {
      setEditTitle(selectedItemDetail.title || '');
      setEditCategory(selectedItemDetail.category || 'General');
      setEditSummary(selectedItemDetail.summary || '');
      setEditContent(selectedItemDetail.content || '');
      setEditCategoryData(selectedItemDetail.categoryData || {});
      setIsEditing(false);
    }
  }, [selectedItemDetail]);

  if (!selectedItemDetail) return null;
  const item = selectedItemDetail;

  const handleCopyContent = () => {
    navigator.clipboard.writeText(item.content || item.summary || '');
    setCopied(true);
    addToast("Content copied to clipboard", "info");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveCorrections = async () => {
    setIsSaving(true);
    try {
      await updateItem(item.id, {
        title: editTitle,
        category: editCategory,
        summary: editSummary,
        content: editContent,
        categoryData: editCategoryData,
      });
      setIsEditing(false);
    } catch (err) {
      // Error toasted in context
    } finally {
      setIsSaving(false);
    }
  };

  const handleConfirmSuggestedReminder = async (rem) => {
    setConfirmingReminderId(rem.id);
    try {
      await confirmReminder(item.id, {
        title: rem.title,
        dueDate: rem.dueDate,
        priority: rem.priority || 'normal',
      });
    } finally {
      setConfirmingReminderId(null);
    }
  };

  const formattedDate = item.createdAt 
    ? format(new Date(item.createdAt), 'PPP p')
    : 'Unknown Date';

  const catData = isEditing ? editCategoryData : (item.categoryData || {});

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div 
        className="w-full max-w-3xl bg-dark-card border border-dark-border rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-dark-border/80 bg-dark-surface/80">
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-xs px-2.5 py-1 rounded-lg bg-accent/15 text-accent-light border border-accent/30 font-semibold uppercase tracking-wider shrink-0">
              {item.imageCategory ? item.imageCategory.replace('_', ' ') : item.type}
            </span>
            <div className="truncate">
              {isEditing ? (
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="text-base font-bold text-white bg-dark-bg border border-dark-border focus:border-accent rounded-lg px-2.5 py-1 outline-none w-full max-w-md"
                />
              ) : (
                <h3 className="text-base font-bold text-white truncate">{item.title}</h3>
              )}
              <p className="text-xs text-app-subtle">{formattedDate} • {item.category}</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {/* Edit / Correct Fields Button (Requirement 13) */}
            <button
              onClick={() => {
                if (isEditing) {
                  handleSaveCorrections();
                } else {
                  setIsEditing(true);
                }
              }}
              disabled={isSaving}
              className={`p-2 rounded-xl border transition-colors cursor-pointer flex items-center gap-1 text-xs font-semibold ${
                isEditing 
                  ? 'bg-accent/20 border-accent text-accent-light hover:bg-accent/30' 
                  : 'border-dark-border hover:bg-dark-hover text-app-subtle hover:text-white'
              }`}
              title={isEditing ? "Save Corrections" : "Correct / Edit Inaccurate Fields"}
            >
              {isEditing ? (
                <>
                  <Save className="w-4 h-4 text-accent-light" />
                  <span className="hidden sm:inline">Save</span>
                </>
              ) : (
                <>
                  <Edit3 className="w-4 h-4" />
                  <span className="hidden sm:inline">Edit</span>
                </>
              )}
            </button>

            <button
              onClick={() => toggleFavorite(item.id)}
              className={`p-2 rounded-xl border border-dark-border hover:bg-dark-hover transition-colors cursor-pointer ${
                item.favorite ? 'text-amber-400 border-amber-400/40' : 'text-app-subtle hover:text-white'
              }`}
              title="Toggle Favorite"
            >
              <Star className={`w-4 h-4 ${item.favorite ? 'fill-amber-400' : ''}`} />
            </button>

            <button
              onClick={handleCopyContent}
              className="p-2 rounded-xl border border-dark-border hover:bg-dark-hover text-app-subtle hover:text-white transition-colors cursor-pointer"
              title="Copy text"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            </button>

            <button
              onClick={() => deleteItem(item.id)}
              className="p-2 rounded-xl border border-dark-border hover:bg-rose-500/15 text-app-subtle hover:text-rose-400 transition-colors cursor-pointer"
              title="Delete item"
            >
              <Trash2 className="w-4 h-4" />
            </button>

            <button
              onClick={closeDetail}
              className="p-2 rounded-xl text-app-subtle hover:text-white hover:bg-dark-hover transition-colors cursor-pointer ml-1"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Sensitive Identity Document Notice (Requirement 15) */}
          {item.isSensitive && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2.5">
              <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0" />
              <span>
                <strong>Confidential Identity Record:</strong> Access is restricted solely to your authenticated account. Identifiers are masked.
              </span>
            </div>
          )}

          {/* AI Executive Summary Card */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-accent/10 via-dark-surface to-accent-teal/10 border border-accent/25">
            <div className="flex items-center gap-2 text-xs font-semibold text-accent-light uppercase tracking-wider mb-1.5">
              <Sparkles className="w-4 h-4 text-accent-light" />
              <span>AI Executive Summary</span>
            </div>
            {isEditing ? (
              <textarea
                rows={3}
                value={editSummary}
                onChange={(e) => setEditSummary(e.target.value)}
                className="w-full bg-dark-bg/80 border border-dark-border focus:border-accent rounded-lg p-2.5 text-xs text-app-text outline-none resize-y"
              />
            ) : (
              <p className="text-sm text-app-text leading-relaxed font-sans">
                {item.summary}
              </p>
            )}
          </div>

          {/* Type: Image / OCR Section */}
          {item.type === 'image' && (
            <div className="space-y-4">
              {item.imageUrl && (
                <div className="rounded-2xl overflow-hidden border border-dark-border bg-dark-bg max-h-80 flex items-center justify-center p-2 relative group">
                  <img
                    src={item.imageUrl}
                    alt={item.title}
                    className="w-full h-full object-contain max-h-80 rounded-xl"
                  />
                  {item.fileSize && (
                    <div className="absolute bottom-4 right-4 bg-black/70 backdrop-blur-md px-2.5 py-1 rounded-lg border border-white/10 text-[11px] text-white font-mono">
                      {item.fileSize}
                    </div>
                  )}
                </div>
              )}

              {/* Category-Specific Extracted Fields Table (Requirement 7 & 13) */}
              {catData && Object.keys(catData).length > 0 && (
                <div className="p-4 rounded-xl bg-dark-surface/60 border border-dark-border space-y-3">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="text-xs font-semibold text-accent-light uppercase tracking-wider flex items-center gap-1.5">
                        <Layers className="w-3.5 h-3.5" />
                        <span>Extracted {item.imageCategory ? item.imageCategory.replace('_', ' ').toUpperCase() : 'DOCUMENT'} Details</span>
                      </h4>
                      {item.subtype && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-palette-sand/30 text-palette-clay border border-palette-clay/30 font-medium">
                          {item.subtype.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {item.needs_review && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-palette-sand/40 text-palette-clay border border-palette-clay/35 font-medium flex items-center gap-1">
                          Needs Review
                        </span>
                      )}
                      {(item.confidence || item.ocrConfidence) && (
                        <span className="text-[11px] px-2 py-0.5 rounded-full bg-palette-mist/25 text-palette-slate dark:text-palette-mist border border-palette-mist/40 font-medium">
                          {Math.round((item.confidence && item.confidence <= 1 ? item.confidence * 100 : item.ocrConfidence || 85))}% Confidence
                        </span>
                      )}
                    </div>
                  </div>

                  {item.reason && (
                    <p className="text-[11px] text-app-subtle italic bg-dark-bg/60 p-2 rounded-lg border border-dark-border/50">
                      <span className="font-semibold text-app-muted not-italic">Classification Context:</span> {item.reason}
                    </p>
                  )}

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    {Object.entries(catData).map(([key, val]) => {
                      if (val === null || val === undefined || key.startsWith("normalized")) return null;
                      const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                      
                      return (
                        <div key={key} className="p-2.5 rounded-lg bg-dark-bg/80 border border-dark-border">
                          <span className="text-[10px] text-app-subtle uppercase tracking-wider block font-semibold mb-0.5">
                            {label}
                          </span>
                          {isEditing ? (
                            <input
                              type="text"
                              value={typeof val === 'string' ? val : JSON.stringify(val)}
                              onChange={(e) => setEditCategoryData({ ...editCategoryData, [key]: e.target.value })}
                              className="w-full bg-dark-surface border border-dark-border rounded px-2 py-1 text-xs text-white outline-none"
                            />
                          ) : (
                            <span className="text-white font-medium break-words font-mono">
                              {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Suggested Reminders (Requirement 12) */}
              {item.suggestedReminders && item.suggestedReminders.length > 0 && (
                <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Suggested Reminders from Extracted Dates</span>
                    </span>
                    <span className="text-[11px] text-app-subtle">
                      Requires user confirmation
                    </span>
                  </div>

                  <div className="space-y-2">
                    {item.suggestedReminders.map((rem) => {
                      const isConfirmed = Boolean(rem.confirmed);
                      return (
                        <div
                          key={rem.id}
                          className="p-3 rounded-xl bg-dark-bg/80 border border-indigo-500/25 flex items-center justify-between gap-3"
                        >
                          <div className="min-w-0">
                            <p className="text-xs font-semibold text-white">{rem.title}</p>
                            <p className="text-[11px] text-indigo-300 font-mono mt-0.5">
                              Due: {new Date(rem.dueDate).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                              {rem.priority === 'urgent' && ' • Urgent'}
                            </p>
                          </div>

                          {isConfirmed ? (
                            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shrink-0">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>In Reminders</span>
                            </span>
                          ) : (
                            <button
                              onClick={() => handleConfirmSuggestedReminder(rem)}
                              disabled={confirmingReminderId === rem.id}
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-500/20 text-indigo-200 border border-indigo-500/40 hover:bg-indigo-500/30 transition-colors cursor-pointer shrink-0 disabled:opacity-50"
                            >
                              <Plus className="w-3.5 h-3.5" />
                              <span>Add to Reminders</span>
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* OCR Text Extraction View */}
              <div>
                <p className="text-xs font-semibold text-app-muted uppercase tracking-wider mb-1.5 flex items-center justify-between">
                  <span>OCR Extracted Text (Structure Preserved)</span>
                  {item.ocrDetails?.wordCount && (
                    <span className="text-[11px] text-app-subtle font-normal lowercase">
                      {item.ocrDetails.lineCount} lines • {item.ocrDetails.wordCount} words
                    </span>
                  )}
                </p>
                {isEditing ? (
                  <textarea
                    rows={6}
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="w-full text-xs text-app-text bg-dark-bg p-3.5 rounded-xl border border-dark-border focus:border-accent font-mono leading-relaxed outline-none resize-y"
                  />
                ) : (
                  <div className="text-xs text-app-text bg-dark-bg p-3.5 rounded-xl border border-dark-border font-mono leading-relaxed whitespace-pre-wrap max-h-60 overflow-y-auto">
                    {item.content || item.rawOcrText || "No readable text detected in this image."}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Type: Audio / Voice Memo */}
          {item.type === 'voice' && (
            <div className="p-5 rounded-2xl bg-dark-bg border border-dark-border space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setIsPlayingAudio(!isPlayingAudio)}
                    className="w-12 h-12 rounded-full bg-accent hover:bg-accent-hover text-white flex items-center justify-center shadow-glow-sm transition-transform active:scale-95 cursor-pointer"
                  >
                    {isPlayingAudio ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
                  </button>
                  <div>
                    <p className="text-sm font-semibold text-white">Recorded Voice Memo</p>
                    <p className="text-xs text-app-subtle">Duration: {item.duration || '02:30'}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-1">
                <div className="w-full bg-dark-border h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-accent to-accent-teal h-full transition-all duration-300"
                    style={{ width: `${isPlayingAudio ? 65 : audioProgress}%` }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-app-subtle font-mono">
                  <span>01:12</span>
                  <span>{item.duration || '02:30'}</span>
                </div>
              </div>

              <div className="pt-2">
                <p className="text-xs font-semibold text-app-muted uppercase tracking-wider mb-1">
                  AI Transcription
                </p>
                <p className="text-xs text-app-text bg-dark-surface/60 p-3 rounded-xl border border-dark-border/60 leading-relaxed font-mono">
                  {item.content}
                </p>
              </div>
            </div>
          )}

          {/* Type: Document / PDF */}
          {(item.type === 'document' || item.type === 'pdf') && (
            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-dark-bg border border-indigo-500/30 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileUp className="w-7 h-7 text-indigo-400" />
                  <div>
                    <p className="text-sm font-semibold text-white">{item.title}</p>
                    <p className="text-xs text-app-subtle">
                      {item.fileSize || '3.2 MB'} • {item.pages || 14} Pages • PDF Document
                    </p>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 font-medium">
                  Vectorized & Indexed
                </span>
              </div>
              <div className="text-xs text-app-text bg-dark-bg p-4 rounded-xl border border-dark-border leading-relaxed font-mono whitespace-pre-wrap">
                {item.content}
              </div>
            </div>
          )}

          {/* Type: PowerPoint Presentation / PPT */}
          {item.type === 'ppt' && (
            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-dark-bg border border-amber-500/30 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Presentation className="w-7 h-7 text-amber-400" />
                  <div>
                    <p className="text-sm font-semibold text-white">{item.title}</p>
                    <p className="text-xs text-app-subtle">
                      {item.fileSize || '6.4 MB'} • {item.pages || 24} Slides • Presentation Deck
                    </p>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 font-medium">
                  Slide Deck Parsed
                </span>
              </div>
              <div className="text-xs text-app-text bg-dark-bg p-4 rounded-xl border border-dark-border leading-relaxed font-mono whitespace-pre-wrap">
                {item.content}
              </div>
            </div>
          )}

          {/* Type: Word DOCX Document */}
          {item.type === 'docx' && (
            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-dark-bg border border-cyan-500/30 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileCode2 className="w-7 h-7 text-cyan-400" />
                  <div>
                    <p className="text-sm font-semibold text-white">{item.title}</p>
                    <p className="text-xs text-app-subtle">
                      {item.fileSize || '1.5 MB'} • {item.pages || 8} Sections • Word Document
                    </p>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-medium">
                  Outline Extracted
                </span>
              </div>
              <div className="text-xs text-app-text bg-dark-bg p-4 rounded-xl border border-dark-border leading-relaxed font-mono whitespace-pre-wrap">
                {item.content}
              </div>
            </div>
          )}

          {/* Type: Web Link */}
          {item.type === 'link' && (
            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-dark-bg border border-dark-border flex items-center justify-between">
                <div className="flex items-center gap-3 truncate mr-2">
                  <Link2 className="w-6 h-6 text-emerald-400 shrink-0" />
                  <div className="truncate">
                    <p className="text-sm font-semibold text-white truncate">{item.title}</p>
                    <p className="text-xs text-emerald-400/80 truncate">{item.url}</p>
                  </div>
                </div>
                {item.url && (
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/25 transition-colors shrink-0"
                  >
                    <span>Visit</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
              <div className="text-xs text-app-text bg-dark-bg p-4 rounded-xl border border-dark-border leading-relaxed">
                {item.content}
              </div>
            </div>
          )}

          {/* Type: Standard Markdown Note */}
          {item.type === 'note' && (
            <div className="p-4 rounded-xl bg-dark-bg border border-dark-border text-sm text-app-text leading-relaxed font-sans whitespace-pre-wrap">
              {item.content}
            </div>
          )}

          {/* AI Extracted Entities & Detected Reminders */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            {/* Entities & Concepts */}
            <div className="p-4 rounded-xl bg-dark-surface/60 border border-dark-border/80 space-y-2.5">
              <div className="flex items-center gap-2 text-xs font-semibold text-app-subtle uppercase tracking-wider">
                <Layers className="w-3.5 h-3.5 text-accent-light" />
                <span>Extracted Entities & Keywords</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(item.entities?.length > 0 || item.keywords?.length > 0) ? (
                  Array.from(new Set([...(item.entities || []), ...(item.keywords || [])])).map((ent, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2.5 py-1 rounded-lg bg-dark-bg text-app-muted border border-dark-border font-medium"
                    >
                      {ent}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-app-subtle">No specific entities recognized</span>
                )}
              </div>
            </div>

            {/* Confirmed Deadlines & Events */}
            <div className="p-4 rounded-xl bg-dark-surface/60 border border-dark-border/80 space-y-2.5">
              <div className="flex items-center gap-2 text-xs font-semibold text-accent-light uppercase tracking-wider">
                <Calendar className="w-3.5 h-3.5 text-accent-light" />
                <span>Active Deadlines & Action Items</span>
              </div>
              {item.detectedEvents?.length > 0 ? (
                item.detectedEvents.map((ev, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-lg bg-accent/10 border border-accent/30 flex items-center justify-between text-xs"
                  >
                    <div>
                      <p className="font-semibold text-white">{ev.title}</p>
                      <p className="text-[10px] text-accent-light font-mono mt-0.5">
                        {format(new Date(ev.dueDate), 'MMM d, yyyy • h:mm a')}
                      </p>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded uppercase font-bold tracking-wider bg-accent/20 text-accent-light">
                      {ev.priority}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-app-subtle">No active deadlines linked to this item</p>
              )}
            </div>
          </div>

          {/* Tags */}
          {item.tags?.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap pt-2">
              <span className="text-xs text-app-subtle flex items-center gap-1 font-semibold uppercase tracking-wider">
                <Tag className="w-3 h-3" /> Tags:
              </span>
              {item.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2.5 py-0.5 rounded-full bg-dark-bg text-app-muted border border-dark-border"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
